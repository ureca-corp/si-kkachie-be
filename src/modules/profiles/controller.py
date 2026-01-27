"""profiles 도메인 Controller

SPEC 기반 API:
- POST /auth/verify-token (토큰 검증 + 자동 프로필 생성)
- GET /users/me (내 정보 조회)
- PATCH /users/me (내 정보 수정)
- POST /users/me/profile-image (프로필 이미지 업로드 URL 발급)
- DELETE /users/me (회원 탈퇴)
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import (
    get_current_profile,
    verify_supabase_token,
)
from src.core.response import ApiResponse, Status
from src.modules.profiles.models import Profile

from . import service
from .entities import (
    ProfileImageUploadRequest,
    ProfileImageUploadResponse,
    ProfileResponse,
    UpdateProfileRequest,
)

router = APIRouter(tags=["auth", "users"])

bearer_scheme = HTTPBearer(auto_error=False)


@router.post(
    "/auth/verify-token",
    response_model=ApiResponse[ProfileResponse],
    openapi_extra={
        "x-pages": ["login", "signup", "splash"],
        "x-agent-description": "토큰 검증 및 자동 회원가입. 앱 시작 시 또는 로그인/회원가입 플로우에서 Supabase Auth 토큰을 검증하고, 신규 사용자면 프로필을 자동 생성",
    },
)
def verify_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Session = Depends(get_session),
) -> JSONResponse:
    """토큰 검증 (상태 코드 포함)"""
    if credentials is None:
        return JSONResponse(
            status_code=401,
            content={
                "status": Status.ERROR_UNAUTHORIZED,
                "message": "인증 토큰이 필요해요",
                "data": None,
            },
        )

    token = credentials.credentials

    try:
        user_info = verify_supabase_token(token)
    except Exception:
        return JSONResponse(
            status_code=401,
            content={
                "status": Status.ERROR_INVALID_TOKEN,
                "message": "유효하지 않은 토큰이에요",
                "data": None,
            },
        )

    supabase_user_id = UUID(user_info["id"])
    email = user_info["email"]

    profile, is_new_user = service.verify_token_and_get_or_create_profile(
        session, supabase_user_id, email
    )

    response_data = {
        "id": str(profile.id),
        "user_id": str(profile.user_id),
        "email": email,
        "display_name": profile.display_name,
        "preferred_language": profile.preferred_language,
        "profile_image_url": profile.profile_image_url,
        "is_new_user": is_new_user,
    }

    status_code = 201 if is_new_user else 200
    message = "회원가입이 완료됐어요" if is_new_user else "인증에 성공했어요"

    return JSONResponse(
        status_code=status_code,
        content={
            "status": Status.SUCCESS,
            "message": message,
            "data": response_data,
        },
    )


@router.get(
    "/users/me",
    response_model=ApiResponse[ProfileResponse],
    openapi_extra={
        "x-pages": ["profile", "settings", "home"],
        "x-agent-description": "현재 로그인한 사용자의 프로필 정보 조회. 프로필 페이지, 설정 페이지, 홈 화면 헤더에서 사용자 정보 표시할 때 사용",
    },
)
def get_me(
    profile: Annotated[Profile, Depends(get_current_profile)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> ApiResponse[ProfileResponse]:
    """내 정보 조회"""
    # get_current_profile에서 이미 인증 처리됨, credentials는 항상 존재
    if credentials is None:
        from src.core.exceptions import UnauthorizedError
        raise UnauthorizedError("인증 토큰이 필요해요")

    # email은 Supabase Auth에서 가져와야 함
    user_info = verify_supabase_token(credentials.credentials)

    response_data = ProfileResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        email=user_info["email"],
        display_name=profile.display_name,
        preferred_language=profile.preferred_language,
        profile_image_url=profile.profile_image_url,
        created_at=profile.created_at,
    )

    return ApiResponse(
        status=Status.SUCCESS,
        message="조회에 성공했어요",
        data=response_data,
    )


@router.patch(
    "/users/me",
    response_model=ApiResponse[ProfileResponse],
    openapi_extra={
        "x-pages": ["settings", "profile-edit"],
        "x-agent-description": "사용자 프로필 정보 수정. 설정 페이지에서 닉네임, 선호 언어 등을 변경할 때 사용",
    },
)
def update_me(
    request: UpdateProfileRequest,
    profile: Annotated[Profile, Depends(get_current_profile)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Session = Depends(get_session),
) -> ApiResponse[ProfileResponse]:
    """내 정보 수정"""
    # get_current_profile에서 이미 인증 처리됨, credentials는 항상 존재
    if credentials is None:
        from src.core.exceptions import UnauthorizedError
        raise UnauthorizedError("인증 토큰이 필요해요")

    updated_profile = service.update_profile(session, profile, request)

    # email은 Supabase Auth에서 가져옴
    user_info = verify_supabase_token(credentials.credentials)

    response_data = ProfileResponse(
        id=str(updated_profile.id),
        user_id=str(updated_profile.user_id),
        email=user_info["email"],
        display_name=updated_profile.display_name,
        preferred_language=updated_profile.preferred_language,
        profile_image_url=updated_profile.profile_image_url,
    )

    return ApiResponse(
        status=Status.SUCCESS,
        message="정보가 수정됐어요",
        data=response_data,
    )


@router.post(
    "/users/me/profile-image",
    response_model=ApiResponse[ProfileImageUploadResponse],
    openapi_extra={
        "x-pages": ["settings", "profile-edit"],
        "x-agent-description": "프로필 이미지 업로드용 presigned URL 발급. 설정 페이지에서 프로필 사진 변경 시 사용. URL을 받아서 클라이언트에서 직접 스토리지에 업로드",
    },
)
def create_profile_image_upload_url(
    request: ProfileImageUploadRequest,
    profile: Annotated[Profile, Depends(get_current_profile)],
) -> ApiResponse[ProfileImageUploadResponse]:
    """프로필 이미지 업로드 URL 발급"""
    result = service.create_profile_image_upload_url(profile, request)

    return ApiResponse(
        status=Status.SUCCESS,
        message="업로드 URL이 발급됐어요",
        data=ProfileImageUploadResponse(**result),
    )


@router.delete(
    "/users/me",
    response_model=ApiResponse,
    openapi_extra={
        "x-pages": ["settings", "account-delete"],
        "x-agent-description": "회원 탈퇴 처리. 설정 페이지의 계정 삭제 기능에서 사용. 사용자의 모든 데이터가 삭제됨",
    },
)
def delete_me(
    profile: Annotated[Profile, Depends(get_current_profile)],
    session: Session = Depends(get_session),
) -> ApiResponse:
    """회원 탈퇴"""
    service.delete_profile(session, profile)

    return ApiResponse(
        status=Status.SUCCESS,
        message="회원 탈퇴가 완료됐어요",
    )
