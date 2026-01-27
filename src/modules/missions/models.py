"""missions 모델

DDD_CLASS_DIAGRAM.md 기반:
- mission_templates: 미션 템플릿 (관리자 관리)
- mission_steps: 미션 단계 (템플릿에 종속)
- mission_progress: 사용자별 미션 진행 상태
- mission_step_progress: 단계별 진행 상태
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from src.core.enums import MissionStatus


def _utcnow() -> datetime:
    return datetime.now(UTC)


class MissionTemplate(SQLModel, table=True):
    """미션 템플릿"""

    __tablename__ = "mission_templates"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title_ko: str = Field()
    title_en: str = Field()
    description_ko: str = Field()
    description_en: str = Field()
    mission_type: str = Field(unique=True)  # MissionType
    estimated_duration_min: int = Field()
    icon_url: str | None = Field(default=None)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class MissionStep(SQLModel, table=True):
    """미션 단계"""

    __tablename__ = "mission_steps"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    mission_template_id: UUID = Field(foreign_key="mission_templates.id", index=True)
    step_order: int = Field()
    title_ko: str = Field()
    title_en: str = Field()
    description_ko: str = Field()
    description_en: str = Field()
    created_at: datetime = Field(default_factory=_utcnow)


class MissionProgress(SQLModel, table=True):
    """사용자별 미션 진행 상태"""

    __tablename__ = "mission_progress"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(foreign_key="profiles.id", index=True)
    mission_template_id: UUID = Field(foreign_key="mission_templates.id", index=True)
    status: str = Field(default=MissionStatus.NOT_STARTED.value, index=True)
    result: str | None = Field(default=None)  # MissionResult
    current_step: int = Field(default=0)
    started_at: datetime | None = Field(default=None)
    ended_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=_utcnow, index=True)
    updated_at: datetime = Field(default_factory=_utcnow)


class MissionStepProgress(SQLModel, table=True):
    """단계별 진행 상태"""

    __tablename__ = "mission_step_progress"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    mission_progress_id: UUID = Field(foreign_key="mission_progress.id", index=True)
    mission_step_id: UUID = Field(foreign_key="mission_steps.id", index=True)
    is_completed: bool = Field(default=False)
    completed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=_utcnow)
