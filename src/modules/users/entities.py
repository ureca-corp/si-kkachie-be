from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """회원가입 요청"""

    email: EmailStr
    password: str = Field(min_length=8, description="비밀번호 (8자 이상)")
    nickname: str = Field(min_length=2, max_length=50, description="닉네임 (2-50자)")
    nationality: str = Field(
        min_length=2, max_length=2, description="국적 (ISO 3166-1 alpha-2)"
    )
    preferred_language: str = Field(default="en", pattern="^(ko|en)$")


class LoginRequest(BaseModel):
    """로그인 요청"""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """토큰 갱신 요청"""

    refresh_token: str


class UserResponse(BaseModel):
    """사용자 응답"""

    id: str
    email: str
    nickname: str
    nationality: str
    preferred_language: str
    profile_image_url: str | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """토큰 응답"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105
    expires_in: int


class RegisterResponse(BaseModel):
    """회원가입 응답"""

    id: str
    email: str
    nickname: str
    nationality: str
    preferred_language: str


class UpdateProfileRequest(BaseModel):
    """프로필 수정 요청"""

    nickname: str | None = Field(
        default=None, min_length=2, max_length=50, description="닉네임 (2-50자)"
    )
    preferred_language: str | None = Field(default=None, pattern="^(ko|en)$")
    profile_image_url: str | None = Field(default=None, max_length=500)
