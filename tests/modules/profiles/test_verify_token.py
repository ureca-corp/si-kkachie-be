"""POST /auth/verify-token 테스트

TC-U-001: 신규 회원 토큰 검증 (201)
TC-U-002: 기존 회원 토큰 검증 (200)
TC-U-101: 만료된 토큰 (401)
TC-U-102: 토큰 없음 (401)
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.profiles import Profile


class TestVerifyToken:
    """POST /auth/verify-token 테스트"""

    def test_verify_token_new_user_success(
        self,
        client: TestClient,
        session: Session,
    ) -> None:
        """TC-U-001: 신규 회원 토큰 검증 -> 201, is_new_user: true"""
        new_user_id = uuid4()
        mock_user = MagicMock()
        mock_user.id = str(new_user_id)
        mock_user.email = "newuser@example.com"

        mock_response = MagicMock()
        mock_response.user = mock_user

        with patch("src.core.deps.get_supabase_client") as mock_client:
            mock_client.return_value.auth.get_user.return_value = mock_response

            response = client.post(
                "/auth/verify-token",
                headers={"Authorization": "Bearer valid-token"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "회원가입이 완료됐어요"
        assert data["data"]["is_new_user"] is True
        assert data["data"]["email"] == "newuser@example.com"

    def test_verify_token_existing_user_success(
        self,
        client: TestClient,
        session: Session,
        test_profile: Profile,
        test_supabase_user_id,
    ) -> None:
        """TC-U-002: 기존 회원 토큰 검증 -> 200, is_new_user: false"""
        mock_user = MagicMock()
        mock_user.id = str(test_supabase_user_id)
        mock_user.email = "test@example.com"

        mock_response = MagicMock()
        mock_response.user = mock_user

        with patch("src.core.deps.get_supabase_client") as mock_client:
            mock_client.return_value.auth.get_user.return_value = mock_response

            response = client.post(
                "/auth/verify-token",
                headers={"Authorization": "Bearer valid-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "인증에 성공했어요"
        assert data["data"]["is_new_user"] is False

    def test_verify_token_invalid_token(
        self,
        client: TestClient,
    ) -> None:
        """TC-U-101: 만료된/유효하지 않은 토큰 -> 401"""
        with patch("src.core.deps.get_supabase_client") as mock_client:
            mock_client.return_value.auth.get_user.side_effect = Exception(
                "Invalid token"
            )

            response = client.post(
                "/auth/verify-token",
                headers={"Authorization": "Bearer invalid-token"},
            )

        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "ERROR_INVALID_TOKEN"

    def test_verify_token_no_token(
        self,
        client: TestClient,
    ) -> None:
        """TC-U-102: 토큰 없음 -> 401"""
        response = client.post("/auth/verify-token")

        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "ERROR_UNAUTHORIZED"
