from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    """사용자 모델 (외국인 관광객)"""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    nickname: str = Field(max_length=50)
    nationality: str = Field(max_length=2)  # ISO 3166-1 alpha-2
    preferred_language: str = Field(default="en", max_length=5)  # 'ko' | 'en'
    profile_image_url: str | None = Field(default=None, max_length=500)
    last_login_at: datetime | None = Field(default=None)
    login_count: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    deleted_at: datetime | None = Field(default=None)  # soft delete

    def is_deleted(self) -> bool:
        """소프트 삭제 여부 확인"""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """소프트 삭제 처리"""
        self.deleted_at = _utcnow()
        self.is_active = False
