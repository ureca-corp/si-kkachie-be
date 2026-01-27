# TDD 코드 예제

> SKILL.md에서 참조하는 상세 코드 예제

---

## conftest.py 설정

```python
# tests/conftest.py
import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

# 테스트용 인메모리 SQLite
TEST_DATABASE_URL = "sqlite://"  # 인메모리
# 또는 파일 기반: "sqlite:///./test.db"

@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # 인메모리 DB 연결 유지
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    from fastapi.testclient import TestClient
    from src.app.main import app
    from src.core.database import get_session

    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

---

## SQLite ↔ PostgreSQL 호환성

| 항목 | PostgreSQL | SQLite | 대응 |
|------|------------|--------|------|
| UUID | 네이티브 | 문자열 | `String`으로 선언하거나 SQLAlchemy `TypeDecorator` 사용 |
| ARRAY | 지원 | **미지원** | JSON으로 대체하거나 별도 테이블 |
| JSON | JSONB 쿼리 | 제한적 | 복잡한 JSON 쿼리 피하기 |
| 대소문자 | 구분 | 기본 미구분 | `COLLATE NOCASE` 또는 `.lower()` |

**권장 패턴:**
```python
from sqlmodel import SQLModel, Field
from uuid import uuid4

class User(SQLModel, table=True):
    # ✅ UUID를 String으로 저장 (호환성)
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    # ❌ ARRAY 사용 금지
    # tags: list[str] = Field(sa_column=Column(ARRAY(String)))

    # ✅ JSON으로 대체
    tags: dict | None = Field(default=None, sa_column=Column(JSON))
```

---

## 테스트 케이스 설계 예제

```python
# tests/modules/{domain}/test_create.py

import pytest
from httpx import AsyncClient

class TestCreate{Domain}:
    """
    테스트 케이스:
    1. 정상 생성 → 201 + SUCCESS
    2. 필수 필드 누락 → 400 + VALIDATION_ERROR
    3. 중복 데이터 → 409 + ALREADY_EXISTS
    4. 인증 없음 → 401 + UNAUTHORIZED
    """

    async def test_create_success(self, client: AsyncClient):
        """정상 생성 테스트"""
        # Arrange
        payload = {"email": "test@example.com", "name": "테스트"}

        # Act
        response = await client.post("/api/v1/{domain}", json=payload)

        # Assert
        assert response.status_code == 201
        assert response.json()["status"] == "SUCCESS"
```

---

## 최소 구현 예제 (GREEN)

```python
# src/modules/{domain}/api/create.py

@router.post("/", status_code=201)
async def create(
    request: CreateRequest,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse:
    # 최소 구현 - 테스트 통과만 목표
    entity = Model(**request.model_dump())
    session.add(entity)
    await session.commit()

    return ApiResponse(
        status=Status.SUCCESS,
        message="생성됐어요",
        data=Response.model_validate(entity),
    )
```

---

## 테스트 유형별 예제

### 1. 단위 테스트 (Unit)

```python
# 개별 함수 테스트
def test_hash_password():
    result = hash_password("test1234")
    assert verify_password("test1234", result)
```

### 2. 통합 테스트 (Integration)

```python
# API 엔드포인트 + DB 테스트
async def test_create_user_integration(client, session):
    response = await client.post("/api/v1/users", json={...})

    # DB 확인
    user = await session.get(User, response.json()["data"]["id"])
    assert user is not None
```

### 3. 엣지 케이스 테스트

```python
@pytest.mark.parametrize("invalid_email", [
    "",           # 빈 문자열
    "invalid",    # @ 없음
    "@test.com",  # 로컬 파트 없음
    "a" * 256 + "@test.com",  # 너무 긴 이메일
])
async def test_create_invalid_email(client, invalid_email):
    response = await client.post("/api/v1/users", json={"email": invalid_email})
    assert response.status_code == 400
```

---

## 테스트 클린 아키텍처 예제 (CSR 패턴)

### 디렉토리 구조

```
tests/
├── conftest.py              # 공통 픽스처 (DB, Client)
├── factories/               # 테스트 데이터 팩토리
│   ├── __init__.py
│   ├── user_factory.py      # User 생성 팩토리
│   └── order_factory.py     # Order 생성 팩토리
├── fixtures/                # 도메인별 픽스처
│   ├── __init__.py
│   ├── users.py             # User 관련 픽스처
│   └── orders.py            # Order 관련 픽스처
├── helpers/                 # 테스트 유틸리티
│   ├── __init__.py
│   ├── assertions.py        # 커스텀 assertion
│   └── api.py               # API 호출 헬퍼
└── modules/                 # 도메인별 테스트
    ├── users/
    │   ├── __init__.py
    │   ├── conftest.py          # users 전용 픽스처
    │   ├── test_controller.py   # 엔드포인트 테스트 (통합)
    │   └── test_service.py      # 비즈니스 로직 테스트 (단위)
    └── orders/
        ├── __init__.py
        ├── conftest.py
        ├── test_controller.py
        └── test_service.py
```

### factories/ - 테스트 데이터 생성

```python
# tests/factories/user_factory.py
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class UserFactory:
    """User 테스트 데이터 생성 팩토리"""
    id: str = field(default_factory=lambda: str(uuid4()))
    email: str = "test@example.com"
    name: str = "테스트 유저"
    password: str = "password123"

    def build(self) -> dict:
        """Request용 dict 반환"""
        return {
            "email": self.email,
            "name": self.name,
            "password": self.password,
        }

    def create(self, session) -> "User":
        """DB에 저장된 User 반환"""
        from src.modules.users.models import User
        from src.core.security import hash_password

        user = User(
            id=self.id,
            email=self.email,
            name=self.name,
            password_hash=hash_password(self.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
```

### fixtures/ - 재사용 가능한 픽스처

```python
# tests/fixtures/users.py
import pytest
from tests.factories.user_factory import UserFactory

@pytest.fixture
def user_factory():
    """UserFactory 인스턴스 반환"""
    return UserFactory()

@pytest.fixture
def created_user(session, user_factory):
    """DB에 저장된 User 반환"""
    return user_factory.create(session)

@pytest.fixture
def user_payload(user_factory):
    """User 생성 Request payload"""
    return user_factory.build()
```

### helpers/ - 테스트 유틸리티

```python
# tests/helpers/assertions.py
def assert_api_success(response, expected_status: str = "SUCCESS"):
    """API 성공 응답 검증"""
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["status"] == expected_status
    return data

def assert_api_error(response, expected_status: str, expected_code: int = 400):
    """API 에러 응답 검증"""
    assert response.status_code == expected_code
    data = response.json()
    assert data["status"] == expected_status
    return data
```

```python
# tests/helpers/api.py
class UserAPI:
    """User API 호출 헬퍼"""
    BASE_URL = "/api/v1/users"

    def __init__(self, client):
        self.client = client

    def create(self, payload: dict):
        return self.client.post(self.BASE_URL, json=payload)

    def get(self, user_id: str):
        return self.client.get(f"{self.BASE_URL}/{user_id}")

    def list(self, **params):
        return self.client.get(self.BASE_URL, params=params)
```

### 테스트 파일 - 깔끔한 테스트

```python
# tests/modules/users/test_create.py
import pytest
from tests.helpers.assertions import assert_api_success, assert_api_error
from tests.helpers.api import UserAPI

class TestCreateUser:
    """User 생성 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.api = UserAPI(client)

    def test_success(self, user_payload):
        """정상 생성"""
        response = self.api.create(user_payload)
        data = assert_api_success(response, "SUCCESS")
        assert data["data"]["email"] == user_payload["email"]

    def test_duplicate_email(self, created_user, user_factory):
        """중복 이메일"""
        payload = user_factory.build()
        payload["email"] = created_user.email

        response = self.api.create(payload)
        assert_api_error(response, "USER_ALREADY_EXISTS", 409)

    @pytest.mark.parametrize("invalid_email", [
        "",
        "invalid",
        "@test.com",
    ])
    def test_invalid_email(self, user_payload, invalid_email):
        """잘못된 이메일"""
        user_payload["email"] = invalid_email
        response = self.api.create(user_payload)
        assert response.status_code == 422  # Pydantic validation
```
