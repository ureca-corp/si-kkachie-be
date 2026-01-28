"""GET /users/me 테스트

TC-U-003: 내 정보 조회 (200)
"""

from fastapi.testclient import TestClient

from src.modules.profiles import Profile


class TestGetMe:
    """GET /users/me 테스트"""

    def test_get_me_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-U-003: 내 정보 조회 성공"""
        response = auth_client.get("/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "조회에 성공했어요"
        assert data["data"]["display_name"] == "TestUser"
        assert data["data"]["preferred_language"] == "en"
        assert "created_at" in data["data"]

    def test_get_me_unauthorized(
        self,
        client: TestClient,
    ) -> None:
        """인증 없이 조회 시도 -> 401"""
        response = client.get("/users/me")

        assert response.status_code == 401
