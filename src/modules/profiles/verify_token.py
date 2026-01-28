"""POST /auth/verify-token

토큰 검증 및 자동 프로필 생성
- 신규 사용자: 프로필 생성 후 201 반환
- 기존 사용자: 프로필 조회 후 200 반환
"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import verify_supabase_token
from src.core.enums import PreferredLanguage
from src.core.response import Status

from . import _repository as repository
from ._models import Profile

router = APIRouter(tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=False)


class ProfileResponse(BaseModel):
    """프로필 응답"""

    id: str
    user_id: str
    email: str
    display_name: str | None
    preferred_language: str
    profile_image_url: str | None
    is_new_user: bool = False

    model_config = {"from_attributes": True}


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _get_or_create_profile(
    session: Session,
    supabase_user_id: UUID,
    email: str,
) -> tuple[Profile, bool]:
    """프로필 조회 또는 생성

    Returns:
        (Profile, is_new_user)
    """
    profile = repository.get_by_user_id(session, supabase_user_id)

    if profile:
        return profile, False

    new_profile = Profile(
        id=uuid4(),
        user_id=supabase_user_id,
        display_name=None,
        preferred_language=PreferredLanguage.EN.value,
        profile_image_url=None,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    created_profile = repository.create(session, new_profile)
    return created_profile, True


@router.post("/auth/verify-token")
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

    profile, is_new_user = _get_or_create_profile(session, supabase_user_id, email)

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
