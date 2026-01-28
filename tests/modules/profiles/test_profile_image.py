"""POST /users/me/profile-image 테스트

TC-U-005: 프로필 이미지 URL 발급 (200)
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.modules.profiles import Profile


class TestProfileImage:
    """POST /users/me/profile-image 테스트"""

    def test_profile_image_url_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        profile_image_request: dict,
    ) -> None:
        """TC-U-005: 프로필 이미지 업로드 URL 발급 성공"""
        with patch(
            "src.modules.profiles._storage.get_storage_provider"
        ) as mock_storage:
            # get_upload_url 반환값 설정
            mock_storage.return_value.get_upload_url.return_value = (
                "https://storage.supabase.co/presigned-url"
            )

            response = auth_client.post(
                "/users/me/profile-image",
                json=profile_image_request,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "업로드 URL이 발급됐어요"
        assert "upload_url" in data["data"]
        assert "public_url" in data["data"]
        assert "expires_in" in data["data"]
