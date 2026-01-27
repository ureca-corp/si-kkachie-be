"""의존성 주입 (Supabase Auth 기반)

Supabase Auth 사용:
- RPC/RLS 절대 금지 - JWT 검증만 사용
- supabase.auth.get_user(token)으로 토큰 검증
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from src.core.config import settings
from src.core.database import get_session
from src.core.exceptions import TokenInvalidError, UnauthorizedError
from src.modules.profiles.models import Profile

# JWT Bearer 토큰 스킴 (Authorization: Bearer <token>)
bearer_scheme = HTTPBearer(auto_error=False)


def get_supabase_client():
    """Supabase 클라이언트 반환"""
    from supabase import create_client

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def _extract_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    """Bearer 토큰 추출"""
    if credentials is None:
        raise UnauthorizedError("인증 토큰이 필요해요")
    return credentials.credentials


def verify_supabase_token(token: str) -> dict:
    """Supabase 토큰 검증 후 사용자 정보 반환

    Returns:
        {"id": "supabase-user-id", "email": "user@example.com"}
    """
    try:
        client = get_supabase_client()
        response = client.auth.get_user(token)

        if response.user is None:
            raise TokenInvalidError("유효하지 않은 토큰이에요")

        return {
            "id": response.user.id,
            "email": response.user.email,
        }
    except Exception as e:
        raise TokenInvalidError("유효하지 않은 토큰이에요") from e


def get_current_supabase_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> UUID:
    """현재 인증된 Supabase 사용자 ID 반환 (DB 조회 없음)"""
    token = _extract_token(credentials)
    user_info = verify_supabase_token(token)
    return UUID(user_info["id"])


def get_current_profile(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> Profile:
    """현재 인증된 사용자의 프로필 반환"""
    token = _extract_token(credentials)
    user_info = verify_supabase_token(token)
    supabase_user_id = UUID(user_info["id"])

    # profiles 테이블에서 프로필 조회
    profile = session.exec(
        select(Profile).where(Profile.user_id == supabase_user_id)
    ).first()

    if profile is None:
        raise UnauthorizedError("프로필을 찾을 수 없어요")

    return profile


# 타입 별칭
CurrentSupabaseUserId = Annotated[UUID, Depends(get_current_supabase_user_id)]
CurrentProfile = Annotated[Profile, Depends(get_current_profile)]
DbSession = Annotated[Session, Depends(get_session)]
