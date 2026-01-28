"""DELETE /users/me 테스트

TC-U-006: 회원 탈퇴 (200)
"""

from fastapi.testclient import TestClient

from src.modules.profiles import Profile


class TestDeleteMe:
    """DELETE /users/me 테스트"""

    def test_delete_me_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-U-006: 회원 탈퇴 성공"""
        response = auth_client.delete("/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "회원 탈퇴가 완료됐어요"

    def test_delete_me_unauthorized(
        self,
        client: TestClient,
    ) -> None:
        """인증 없이 탈퇴 시도 -> 401"""
        response = client.delete("/users/me")

        assert response.status_code == 401
