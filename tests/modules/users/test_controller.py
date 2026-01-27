from fastapi.testclient import TestClient

from src.modules.users.models import User


def test_register_success(client: TestClient) -> None:
    """회원가입 성공 테스트"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "nickname": "NewUser",
            "nationality": "US",
            "preferred_language": "en",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == "newuser@example.com"
    assert data["data"]["nickname"] == "NewUser"
    assert data["data"]["nationality"] == "US"


def test_register_duplicate_email(client: TestClient, test_user: User) -> None:
    """중복 이메일 회원가입 실패 테스트"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "password": "password123",
            "nickname": "AnotherUser",
            "nationality": "KR",
            "preferred_language": "ko",
        },
    )

    assert response.status_code == 409
    assert response.json()["status"] == "EMAIL_ALREADY_EXISTS"


def test_login_success(client: TestClient, test_user: User) -> None:
    """로그인 성공 테스트"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient, test_user: User) -> None:
    """잘못된 비밀번호 로그인 실패 테스트"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["status"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_user(client: TestClient) -> None:
    """존재하지 않는 사용자 로그인 실패 테스트"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["status"] == "INVALID_CREDENTIALS"


def test_get_profile(auth_client: TestClient) -> None:
    """프로필 조회 테스트"""
    response = auth_client.get("/api/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["nickname"] == "TestUser"


def test_get_profile_unauthorized(client: TestClient) -> None:
    """인증되지 않은 프로필 조회 실패 테스트"""
    response = client.get("/api/users/me")

    assert response.status_code == 401


def test_update_profile(auth_client: TestClient) -> None:
    """프로필 수정 테스트"""
    response = auth_client.patch(
        "/api/users/me",
        json={
            "nickname": "UpdatedNickname",
            "preferred_language": "en",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["nickname"] == "UpdatedNickname"
    assert data["data"]["preferred_language"] == "en"


def test_refresh_token(client: TestClient, test_user: User) -> None:
    """토큰 갱신 테스트"""
    # 먼저 로그인하여 refresh_token 획득
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "password123",
        },
    )
    refresh_token = login_response.json()["data"]["refresh_token"]

    # refresh_token으로 새 토큰 발급
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


def test_delete_account(auth_client: TestClient) -> None:
    """회원 탈퇴 테스트"""
    response = auth_client.delete("/api/users/me")

    assert response.status_code == 200
