from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from src.core.database import get_session
from src.core.exceptions import TokenInvalidError, UnauthorizedError
from src.external.auth import get_auth_provider
from src.modules.users.models import User

# JWT Bearer 토큰 스킴 (Authorization: Bearer <token>)
bearer_scheme = HTTPBearer(auto_error=False)


def _extract_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    """Bearer 토큰 추출"""
    if credentials is None:
        raise UnauthorizedError("인증 토큰이 필요해요")
    return credentials.credentials


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> UUID:
    """현재 인증된 사용자 ID 반환 (DB 조회 없음)"""
    token = _extract_token(credentials)
    auth_provider = get_auth_provider()
    payload = auth_provider.verify_token(token)

    if payload is None:
        raise TokenInvalidError()

    user_id = payload.get("sub")
    if user_id is None:
        raise TokenInvalidError()

    return UUID(user_id)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """현재 인증된 사용자 반환"""
    token = _extract_token(credentials)
    auth_provider = get_auth_provider()
    payload = auth_provider.verify_token(token)

    if payload is None:
        raise TokenInvalidError()

    user_id = payload.get("sub")
    if user_id is None:
        raise TokenInvalidError()

    # soft delete 된 사용자 제외
    user = session.exec(
        select(User).where(User.id == UUID(user_id), User.deleted_at.is_(None))
    ).first()

    if user is None:
        raise UnauthorizedError("사용자를 찾을 수 없어요")

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """현재 활성화된 사용자 반환"""
    if not current_user.is_active:
        raise UnauthorizedError("비활성화된 계정이에요")
    return current_user


# 타입 별칭
CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
DbSession = Annotated[Session, Depends(get_session)]
