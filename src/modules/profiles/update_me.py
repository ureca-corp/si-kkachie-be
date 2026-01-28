"""PATCH /users/me

내 정보 수정
"""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import get_current_profile, verify_supabase_token
from src.core.enums import PreferredLanguage
from src.core.exceptions import UnauthorizedError
from src.core.response import ApiResponse, Status

from . import _repository as repository
from ._models import Profile

router = APIRouter(tags=["users"])

bearer_scheme = HTTPBearer(auto_error=False)


class UpdateProfileRequest(BaseModel):
    """프로필 수정 요청"""

    display_name: str | None = Field(default=None, min_length=2, max_length=50)
    preferred_language: str | None = None

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is not None and v not in [lang.value for lang in PreferredLanguage]:
            msg = "지원하지 않는 언어에요"
            raise ValueError(msg)
        return v


class ProfileResponse(BaseModel):
    """프로필 응답"""

    id: str
    user_id: str
    email: str
    display_name: str | None
    preferred_language: str
    profile_image_url: str | None

    model_config = {"from_attributes": True}


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _update_profile(
    session: Session,
    profile: Profile,
    request: UpdateProfileRequest,
) -> Profile:
    """프로필 수정"""
    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(profile, key, value)

    profile.updated_at = _utcnow()
    return repository.update(session, profile)


@router.patch("/users/me", response_model=ApiResponse[ProfileResponse])
def update_me(
    request: UpdateProfileRequest,
    profile: Annotated[Profile, Depends(get_current_profile)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Session = Depends(get_session),
) -> ApiResponse[ProfileResponse]:
    """내 정보 수정"""
    if credentials is None:
        raise UnauthorizedError("인증 토큰이 필요해요")

    updated_profile = _update_profile(session, profile, request)

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
