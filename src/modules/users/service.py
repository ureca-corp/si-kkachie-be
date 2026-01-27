from uuid import UUID

from sqlmodel import Session

from src.core.config import settings
from src.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from src.core.response import Status
from src.external.auth import get_auth_provider

from . import repository
from .entities import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
)
from .models import User


def register(session: Session, request: RegisterRequest) -> RegisterResponse:
    """회원가입"""
    auth_provider = get_auth_provider()

    # 이메일 중복 검증 (삭제된 사용자 포함)
    existing = repository.get_by_email_include_deleted(session, request.email)
    if existing:
        raise ConflictError(
            message="This email is already registered",
            status=Status.EMAIL_ALREADY_EXISTS,
        )

    # 사용자 생성
    user = User(
        email=request.email,
        password_hash=auth_provider.hash_password(request.password),
        nickname=request.nickname,
        nationality=request.nationality.upper(),
        preferred_language=request.preferred_language,
    )
    created = repository.create(session, user)

    return RegisterResponse(
        id=str(created.id),
        email=created.email,
        nickname=created.nickname,
        nationality=created.nationality,
        preferred_language=created.preferred_language,
    )


def login(session: Session, request: LoginRequest) -> TokenResponse:
    """로그인"""
    auth_provider = get_auth_provider()

    # 사용자 조회
    user = repository.get_by_email(session, request.email)
    if not user:
        raise UnauthorizedError(
            message="Invalid email or password",
            status=Status.INVALID_CREDENTIALS,
        )

    # 비밀번호 검증
    if not auth_provider.verify_password(request.password, user.password_hash):
        raise UnauthorizedError(
            message="Invalid email or password",
            status=Status.INVALID_CREDENTIALS,
        )

    # 비활성 사용자 체크
    if not user.is_active:
        raise UnauthorizedError(
            message="Account is deactivated",
            status=Status.USER_INACTIVE,
        )

    # 로그인 정보 업데이트
    repository.update_login(session, user)

    # 토큰 생성
    access_token = auth_provider.create_token(str(user.id))
    refresh_token = auth_provider.create_token(
        str(user.id),
        expires_minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",  # noqa: S106
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def refresh_token(session: Session, request: RefreshRequest) -> TokenResponse:
    """토큰 갱신"""
    auth_provider = get_auth_provider()

    # 리프레시 토큰 검증
    payload = auth_provider.verify_token(request.refresh_token)
    if not payload:
        raise UnauthorizedError(
            message="Please login again",
            status=Status.TOKEN_INVALID,
        )

    # 사용자 조회
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(
            message="Please login again",
            status=Status.TOKEN_INVALID,
        )

    user = repository.get_by_id(session, UUID(user_id))
    if not user or not user.is_active:
        raise UnauthorizedError(
            message="Account not found or deactivated",
            status=Status.USER_NOT_FOUND,
        )

    # 새 토큰 생성
    access_token = auth_provider.create_token(str(user.id))
    refresh_token = auth_provider.create_token(
        str(user.id),
        expires_minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",  # noqa: S106
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def get_profile(session: Session, user_id: UUID) -> UserResponse:
    """프로필 조회"""
    user = repository.get_by_id(session, user_id)
    if not user:
        raise NotFoundError(
            message="User not found",
            status=Status.USER_NOT_FOUND,
        )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        nickname=user.nickname,
        nationality=user.nationality,
        preferred_language=user.preferred_language,
        profile_image_url=user.profile_image_url,
    )


def update_profile(
    session: Session, user_id: UUID, request: UpdateProfileRequest
) -> UserResponse:
    """프로필 수정"""
    user = repository.get_by_id(session, user_id)
    if not user:
        raise NotFoundError(
            message="User not found",
            status=Status.USER_NOT_FOUND,
        )

    # 변경된 필드만 업데이트
    if request.nickname is not None:
        user.nickname = request.nickname
    if request.preferred_language is not None:
        user.preferred_language = request.preferred_language
    if request.profile_image_url is not None:
        user.profile_image_url = request.profile_image_url

    updated = repository.update(session, user)

    return UserResponse(
        id=str(updated.id),
        email=updated.email,
        nickname=updated.nickname,
        nationality=updated.nationality,
        preferred_language=updated.preferred_language,
        profile_image_url=updated.profile_image_url,
    )


def delete_account(session: Session, user_id: UUID) -> None:
    """회원 탈퇴 (소프트 삭제)"""
    user = repository.get_by_id(session, user_id)
    if not user:
        raise NotFoundError(
            message="User not found",
            status=Status.USER_NOT_FOUND,
        )

    repository.soft_delete(session, user)
