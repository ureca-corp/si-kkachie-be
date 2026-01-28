"""translations 모델

DDD_CLASS_DIAGRAM.md 기반:
- 번역 기록 영구 저장
- text/voice 두 가지 타입
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from src.core.enums import TranslationType


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Translation(SQLModel, table=True):
    """번역 기록"""

    __tablename__ = "translations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(foreign_key="profiles.id", index=True)
    source_text: str = Field()
    translated_text: str = Field()
    source_lang: str = Field(max_length=5)
    target_lang: str = Field(max_length=5)
    translation_type: str = Field(default=TranslationType.TEXT.value)
    mission_progress_id: UUID | None = Field(
        default=None, foreign_key="mission_progress.id"
    )
    audio_url: str | None = Field(default=None)
    duration_ms: int | None = Field(default=None)
    confidence_score: float | None = Field(default=None)
    created_at: datetime = Field(default_factory=_utcnow, index=True)
