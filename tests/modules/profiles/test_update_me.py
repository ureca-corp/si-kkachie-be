"""PATCH /users/me 테스트

TC-U-004: 내 정보 수정 (200)
TC-U-103: 잘못된 display_name (400)
TC-U-104: 지원하지 않는 언어 (400)
"""

from fastapi.testclient import TestClient

from src.modules.profiles import Profile


class TestUpdateMe:
    """PATCH /users/me 테스트"""

    def test_update_me_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        update_profile_data: dict,
    ) -> None:
        """TC-U-004: 내 정보 수정 성공"""
        response = auth_client.patch("/users/me", json=update_profile_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "정보가 수정됐어요"
        assert data["data"]["display_name"] == "새 이름"
        assert data["data"]["preferred_language"] == "ko"

    def test_update_me_invalid_display_name(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-U-103: 잘못된 display_name (1자) -> 400"""
        response = auth_client.patch(
            "/users/me",
            json={"display_name": "A"},  # 2자 미만
        )

        assert response.status_code == 422  # Pydantic validation
        data = response.json()
        assert data["status"] == "VALIDATION_FAILED"

    def test_update_me_invalid_language(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-U-104: 지원하지 않는 언어 -> 400"""
        response = auth_client.patch(
            "/users/me",
            json={"preferred_language": "jp"},  # ko 또는 en만 지원
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "VALIDATION_FAILED"
