"""GET /users/me

내 정보 조회
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.core.deps import get_current_profile, verify_supabase_token
from src.core.exceptions import UnauthorizedError
from src.core.response import ApiResponse, Status

from ._models import Profile

router = APIRouter(tags=["users"])

bearer_scheme = HTTPBearer(auto_error=False)


class ProfileResponse(BaseModel):
    """프로필 응답"""

    id: str
    user_id: str
    email: str
    display_name: str | None
    preferred_language: str
    profile_image_url: str | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


@router.get("/users/me", response_model=ApiResponse[ProfileResponse])
def get_me(
    profile: Annotated[Profile, Depends(get_current_profile)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> ApiResponse[ProfileResponse]:
    """내 정보 조회"""
    if credentials is None:
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
