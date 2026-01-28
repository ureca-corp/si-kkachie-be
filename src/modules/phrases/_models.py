"""phrases 모델 (공유)

DDD_CLASS_DIAGRAM.md 기반:
- phrases: 추천 문장 템플릿
- phrase_step_mapping: 미션 단계와 N:M 관계
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Phrase(SQLModel, table=True):
    """추천 문장"""

    __tablename__ = "phrases"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    text_ko: str = Field()
    text_en: str = Field()
    category: str = Field(index=True)  # PhraseCategory
    usage_count: int = Field(default=0, index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class PhraseStepMapping(SQLModel, table=True):
    """문장-단계 매핑 (N:M)"""

    __tablename__ = "phrase_step_mapping"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    phrase_id: UUID = Field(foreign_key="phrases.id", index=True)
    mission_step_id: UUID = Field(foreign_key="mission_steps.id", index=True)
    display_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=_utcnow)
