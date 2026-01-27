from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.app.main import app
from src.core.database import get_session
from src.external.auth import get_auth_provider
from src.modules.users.models import User


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """테스트용 인메모리 데이터베이스 세션"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """테스트 클라이언트"""

    def get_session_override() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """테스트용 사용자"""
    auth_provider = get_auth_provider()

    user = User(
        id=uuid4(),
        email="test@example.com",
        nickname="TestUser",
        nationality="KR",
        preferred_language="ko",
        password_hash=auth_provider.hash_password("password123"),
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture(name="auth_client")
def auth_client_fixture(
    client: TestClient,
    test_user: User,
) -> TestClient:
    """인증된 테스트 클라이언트"""
    auth_provider = get_auth_provider()
    token = auth_provider.create_token(str(test_user.id))
    client.headers["Authorization"] = f"Bearer {token}"
    return client
