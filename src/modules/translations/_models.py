"""translations 모델

DDD_CLASS_DIAGRAM.md 기반:
- 번역 기록 영구 저장
- text/voice 두 가지 타입
- 스레드 기반 대화 관리
- 카테고리 컨텍스트 번역
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from src.core.enums import TranslationType


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ─────────────────────────────────────────────────
# Category Models (마스터 데이터)
# ─────────────────────────────────────────────────


class TranslationPrimaryCategory(SQLModel, table=True):
    """1차 카테고리 (장소 유형)"""

    __tablename__ = "translation_primary_categories"

    code: str = Field(primary_key=True, max_length=10)  # FD6, CE7, etc.
    name_ko: str = Field(max_length=50)
    name_en: str = Field(max_length=50)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class TranslationSubCategory(SQLModel, table=True):
    """2차 카테고리 (상황/의도)"""

    __tablename__ = "translation_sub_categories"

    code: str = Field(primary_key=True, max_length=50)  # ordering, payment, etc.
    name_ko: str = Field(max_length=50)
    name_en: str = Field(max_length=50)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class TranslationCategoryMapping(SQLModel, table=True):
    """1차-2차 카테고리 매핑 (유효한 조합 정의)"""

    __tablename__ = "translation_category_mappings"
    __table_args__ = (
        UniqueConstraint("primary_code", "sub_code", name="uq_category_mapping"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    primary_code: str = Field(
        foreign_key="translation_primary_categories.code", max_length=10
    )
    sub_code: str = Field(
        foreign_key="translation_sub_categories.code", max_length=50
    )


class TranslationContextPrompt(SQLModel, table=True):
    """카테고리별 AI 번역 컨텍스트 프롬프트"""

    __tablename__ = "translation_context_prompts"
    __table_args__ = (
        UniqueConstraint("primary_code", "sub_code", name="uq_context_prompt"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    primary_code: str = Field(
        foreign_key="translation_primary_categories.code", max_length=10
    )
    sub_code: str = Field(
        foreign_key="translation_sub_categories.code", max_length=50
    )
    prompt_ko: str = Field()  # 한국어 프롬프트
    prompt_en: str = Field()  # 영어 프롬프트
    keywords: str | None = Field(default=None)  # 키워드 (콤마 구분)
    is_active: bool = Field(default=True)


# ─────────────────────────────────────────────────
# Thread Model (사용자 대화 스레드)
# ─────────────────────────────────────────────────


class TranslationThread(SQLModel, table=True):
    """번역 대화 스레드"""

    __tablename__ = "translation_threads"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(foreign_key="profiles.id", index=True)
    primary_category: str = Field(
        foreign_key="translation_primary_categories.code", max_length=10
    )
    sub_category: str = Field(
        foreign_key="translation_sub_categories.code", max_length=50
    )
    created_at: datetime = Field(default_factory=_utcnow, index=True)
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)  # Soft delete


# ─────────────────────────────────────────────────
# Translation Model (기존 + 확장)
# ─────────────────────────────────────────────────


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

    # 신규 필드: 스레드 및 컨텍스트
    thread_id: UUID | None = Field(
        default=None, foreign_key="translation_threads.id", index=True
    )
    context_primary: str | None = Field(default=None, max_length=10)
    context_sub: str | None = Field(default=None, max_length=50)
