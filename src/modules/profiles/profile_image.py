"""POST /users/me/profile-image

프로필 이미지 업로드 URL 발급
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.core.deps import get_current_profile
from src.core.response import ApiResponse, Status

from . import _storage as storage
from ._models import Profile

router = APIRouter(tags=["users"])


class ProfileImageUploadRequest(BaseModel):
    """프로필 이미지 업로드 URL 요청"""

    file_name: str = Field(min_length=1)
    content_type: str = Field(pattern=r"^image/(jpeg|png|gif|webp)$")


class ProfileImageUploadResponse(BaseModel):
    """프로필 이미지 업로드 URL 응답"""

    upload_url: str
    public_url: str
    expires_in: int = 3600


@router.post(
    "/users/me/profile-image",
    response_model=ApiResponse[ProfileImageUploadResponse],
)
def create_profile_image_upload_url(
    request: ProfileImageUploadRequest,
    profile: Annotated[Profile, Depends(get_current_profile)],
) -> ApiResponse[ProfileImageUploadResponse]:
    """프로필 이미지 업로드 URL 발급"""
    result = storage.create_presigned_url(
        profile_id=profile.id,
        file_name=request.file_name,
        content_type=request.content_type,
    )

    return ApiResponse(
        status=Status.SUCCESS,
        message="업로드 URL이 발급됐어요",
        data=ProfileImageUploadResponse(**result),
    )
