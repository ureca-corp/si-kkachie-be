"""profiles 도메인 컨트롤러 테스트

SPEC 기반 테스트 케이스:
- TC-U-001: 신규 회원 토큰 검증 (201)
- TC-U-002: 기존 회원 토큰 검증 (200)
- TC-U-003: 내 정보 조회 (200)
- TC-U-004: 내 정보 수정 (200)
- TC-U-005: 프로필 이미지 URL 발급 (200)
- TC-U-006: 회원 탈퇴 (200)
- TC-U-101: 만료된 토큰 (401)
- TC-U-102: 토큰 없음 (401)
- TC-U-103: 잘못된 display_name (400)
- TC-U-104: 지원하지 않는 언어 (400)
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.profiles.models import Profile


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


class TestProfileImage:
    """POST /users/me/profile-image 테스트"""

    def test_profile_image_url_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        profile_image_request: dict,
    ) -> None:
        """TC-U-005: 프로필 이미지 업로드 URL 발급 성공"""
        with patch("src.modules.profiles.service.get_storage_provider") as mock_storage:
            mock_storage.return_value.create_presigned_upload_url.return_value = {
                "upload_url": "https://storage.supabase.co/presigned-url",
                "public_url": "https://storage.supabase.co/public/profile.jpg",
            }

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
