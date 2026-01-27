from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import get_current_user_id
from src.core.response import ApiResponse, Status

from . import service
from .entities import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
)

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=ApiResponse[RegisterResponse])
def register(
    request: RegisterRequest,
    session: Session = Depends(get_session),
) -> ApiResponse[RegisterResponse]:
    """회원가입"""
    result = service.register(session, request)
    return ApiResponse(
        status=Status.SUCCESS,
        message="Welcome! Your account has been created.",
        data=result,
    )


@router.post("/auth/login", response_model=ApiResponse[TokenResponse])
def login(
    request: LoginRequest,
    session: Session = Depends(get_session),
) -> ApiResponse[TokenResponse]:
    """로그인"""
    result = service.login(session, request)
    return ApiResponse(
        status=Status.SUCCESS,
        message="Successfully logged in",
        data=result,
    )


@router.post("/auth/refresh", response_model=ApiResponse[TokenResponse])
def refresh(
    request: RefreshRequest,
    session: Session = Depends(get_session),
) -> ApiResponse[TokenResponse]:
    """토큰 갱신"""
    result = service.refresh_token(session, request)
    return ApiResponse(
        status=Status.SUCCESS,
        message="Token refreshed",
        data=result,
    )


@router.get("/users/me", response_model=ApiResponse[UserResponse])
def get_profile(
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
) -> ApiResponse[UserResponse]:
    """내 프로필 조회"""
    result = service.get_profile(session, user_id)
    return ApiResponse(
        status=Status.SUCCESS,
        message="Profile retrieved",
        data=result,
    )


@router.patch("/users/me", response_model=ApiResponse[UserResponse])
def update_profile(
    request: UpdateProfileRequest,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
) -> ApiResponse[UserResponse]:
    """프로필 수정"""
    result = service.update_profile(session, user_id, request)
    return ApiResponse(
        status=Status.SUCCESS,
        message="Profile updated",
        data=result,
    )


@router.delete("/users/me", response_model=ApiResponse[None])
def delete_account(
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
) -> ApiResponse[None]:
    """회원 탈퇴"""
    service.delete_account(session, user_id)
    return ApiResponse(
        status=Status.SUCCESS,
        message="Account deleted",
        data=None,
    )
