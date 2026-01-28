"""의존성 주입 (Supabase Auth 기반)

Supabase Auth 사용:
- RPC/RLS 절대 금지 - JWT 검증만 사용
- JWKS 또는 JWT Secret으로 토큰 로컬 검증 (권장)
- 폴백: supabase.auth.get_user(token) API 호출
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlmodel import Session, select

from src.core.config import settings
from src.core.database import get_session
from src.core.exceptions import TokenInvalidError, UnauthorizedError

if TYPE_CHECKING:
    from src.modules.profiles._models import Profile

logger = logging.getLogger(__name__)

# JWT Bearer 토큰 스킴 (Authorization: Bearer <token>)
bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _get_jwks_client() -> PyJWKClient | None:
    """JWKS 클라이언트 (싱글톤, 내부 캐싱 포함)"""
    if settings.SUPABASE_JWKS_URL:
        return PyJWKClient(
            settings.SUPABASE_JWKS_URL,
            cache_jwk_set=True,
            lifespan=3600,  # 1시간 캐싱
        )
    return None


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


def _verify_with_jwks(token: str) -> dict | None:
    """JWKS로 JWT 검증 (ES256 비대칭키)"""
    jwks_client = _get_jwks_client()
    if jwks_client is None:
        return None

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            options={"require": ["exp", "sub", "aud"]},
        )
        return {
            "id": payload["sub"],
            "email": payload.get("email"),
        }
    except jwt.ExpiredSignatureError as e:
        raise TokenInvalidError("토큰이 만료되었어요") from e
    except jwt.InvalidAudienceError as e:
        raise TokenInvalidError("유효하지 않은 토큰이에요 (audience)") from e
    except jwt.PyJWTError as e:
        logger.warning("JWKS 검증 실패: %s", e)
        return None


def _verify_with_api(token: str) -> dict:
    """Supabase Auth API로 검증 (폴백)"""
    try:
        client = get_supabase_client()
        response = client.auth.get_user(token)
    except Exception as e:
        raise TokenInvalidError("유효하지 않은 토큰이에요") from e

    if response.user is None:
        raise TokenInvalidError("유효하지 않은 토큰이에요")

    return {
        "id": response.user.id,
        "email": response.user.email,
    }


def verify_supabase_token(token: str) -> dict:
    """Supabase 토큰 검증 후 사용자 정보 반환

    검증 우선순위:
    1. JWKS (ES256) - SUPABASE_JWKS_URL 설정 시 (권장)
    2. Auth API 호출 - 폴백 (네트워크 필요)

    Returns:
        {"id": "supabase-user-id", "email": "user@example.com"}
    """
    # 1. JWKS 검증 시도 (ES256 - 권장)
    result = _verify_with_jwks(token)
    if result:
        return result

    # 2. 폴백: Auth API 호출
    logger.debug("JWKS 미설정, Auth API로 폴백")
    return _verify_with_api(token)


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
    # 런타임 import로 순환 참조 방지
    from src.modules.profiles._models import Profile

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
CurrentProfile = Annotated["Profile", Depends(get_current_profile)]
DbSession = Annotated[Session, Depends(get_session)]
