"""profiles 도메인 Request/Response DTO"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.core.enums import PreferredLanguage


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


class ProfileImageUploadRequest(BaseModel):
    """프로필 이미지 업로드 URL 요청"""

    file_name: str = Field(min_length=1)
    content_type: str = Field(pattern=r"^image/(jpeg|png|gif|webp)$")


class ProfileResponse(BaseModel):
    """프로필 응답"""

    id: str
    user_id: str
    email: str
    display_name: str | None
    preferred_language: str
    profile_image_url: str | None
    is_new_user: bool = False
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProfileImageUploadResponse(BaseModel):
    """프로필 이미지 업로드 URL 응답"""

    upload_url: str
    public_url: str
    expires_in: int = 3600
