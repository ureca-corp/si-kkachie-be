"""profiles 모델 (Supabase auth.users 확장)

DDD_CLASS_DIAGRAM.md 기반:
- auth.users는 Supabase가 관리
- profiles 테이블로 추가 정보만 저장
- UUID v7 사용 (시간순 정렬 가능)
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from src.core.enums import PreferredLanguage


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Profile(SQLModel, table=True):
    """사용자 프로필 (auth.users 확장)"""

    __tablename__ = "profiles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(unique=True, index=True)  # auth.users.id FK
    display_name: str | None = Field(default=None, max_length=50)
    preferred_language: str = Field(default=PreferredLanguage.EN.value, max_length=2)
    profile_image_url: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
