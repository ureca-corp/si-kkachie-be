"""테스트 공통 픽스처

- 기본: 인메모리 SQLite (빠른 단위 테스트)
- DATABASE_URL 환경변수로 PostgreSQL 선택 가능
- Supabase Auth는 모킹, 도메인 테이블은 실제 DB에서 테스트
"""

import os
from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.app.main import app
from src.core.database import get_session


def _utcnow() -> datetime:
    return datetime.now(UTC)


# 테스트용 데이터베이스 URL 결정
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite://",  # 기본값: 인메모리 SQLite
)

# PostgreSQL 사용 여부
_USE_POSTGRES = TEST_DATABASE_URL.startswith("postgresql")


@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    """테스트용 데이터베이스 엔진 (세션 범위)"""
    if _USE_POSTGRES:
        return create_engine(TEST_DATABASE_URL)
    else:
        return create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """테스트용 데이터베이스 세션 (테스트별 격리)"""
    if not _USE_POSTGRES:
        # SQLite: 매 테스트마다 테이블 생성
        SQLModel.metadata.create_all(engine)

    # 트랜잭션 시작 (테스트 격리용)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # 트랜잭션 롤백으로 테스트 데이터 정리
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """테스트 클라이언트 (인증 없음)"""

    def get_session_override() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_supabase_user_id")
def test_supabase_user_id_fixture() -> UUID:
    """Supabase auth.users에서 온 것으로 가정하는 사용자 ID"""
    return uuid4()


@pytest.fixture(name="test_profile")
def test_profile_fixture(session: Session, test_supabase_user_id: UUID):
    """테스트용 프로필 (DB에 저장)"""
    from src.modules.profiles import Profile

    profile = Profile(
        id=uuid4(),
        user_id=test_supabase_user_id,
        display_name="TestUser",
        preferred_language="en",
        profile_image_url=None,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@pytest.fixture(name="mock_supabase_auth")
def mock_supabase_auth_fixture(test_supabase_user_id: UUID):
    """Supabase Auth 모킹"""
    mock_user = MagicMock()
    mock_user.id = str(test_supabase_user_id)
    mock_user.email = "test@example.com"

    mock_response = MagicMock()
    mock_response.user = mock_user

    with patch("src.core.deps.get_supabase_client") as mock_client:
        mock_client.return_value.auth.get_user.return_value = mock_response
        yield mock_client


@pytest.fixture(name="auth_headers")
def auth_headers_fixture() -> dict[str, str]:
    """인증 헤더 (테스트용 토큰)"""
    return {"Authorization": "Bearer test-supabase-token"}


@pytest.fixture(name="auth_client")
def auth_client_fixture(
    client: TestClient,
    mock_supabase_auth: MagicMock,
    auth_headers: dict[str, str],
) -> TestClient:
    """인증된 테스트 클라이언트 (Supabase Auth 모킹)"""
    client.headers.update(auth_headers)
    return client


@pytest.fixture(name="update_profile_data")
def update_profile_data_fixture() -> dict:
    """프로필 수정 요청 데이터"""
    return {
        "display_name": "새 이름",
        "preferred_language": "ko",
    }


@pytest.fixture(name="profile_image_request")
def profile_image_request_fixture() -> dict:
    """프로필 이미지 업로드 요청 데이터"""
    return {
        "file_name": "profile.jpg",
        "content_type": "image/jpeg",
    }
