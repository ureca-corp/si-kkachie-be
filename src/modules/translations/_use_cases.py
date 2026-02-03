"""translations 도메인 Use Cases

클린 아키텍처: Application Layer
- 비즈니스 로직을 캡슐화
- Controller에서 분리하여 재사용성 및 테스트 용이성 확보
- Repository/Service는 인터페이스를 통해 주입 (DIP)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Session

from ._exceptions import (
    InvalidCategoryError,
    ThreadAccessDeniedError,
    ThreadNotFoundError,
)
from ._models import TranslationThread

if TYPE_CHECKING:
    from ._interfaces import (
        ICategoryRepository,
        IContextService,
        IThreadRepository,
        ITranslationRepository,
        ITranslationService,
    )


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ─────────────────────────────────────────────────
# DTOs (Use Case Input/Output)
# ─────────────────────────────────────────────────


@dataclass
class ThreadResult:
    """스레드 결과 DTO"""

    id: UUID
    profile_id: UUID
    primary_category: str
    sub_category: str
    created_at: datetime

    @classmethod
    def from_entity(cls, thread: TranslationThread) -> ThreadResult:
        return cls(
            id=thread.id,
            profile_id=thread.profile_id,
            primary_category=thread.primary_category,
            sub_category=thread.sub_category,
            created_at=thread.created_at,
        )


@dataclass
class TranslationResult:
    """번역 결과 DTO"""

    id: UUID
    profile_id: UUID
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    translation_type: str
    mission_progress_id: UUID | None
    thread_id: UUID | None
    context_primary: str | None
    context_sub: str | None
    audio_url: str | None
    duration_ms: int | None
    confidence_score: float | None
    created_at: datetime


@dataclass
class ThreadDetailResult:
    """스레드 상세 결과 DTO (번역 기록 포함)"""

    id: UUID
    profile_id: UUID
    primary_category: str
    sub_category: str
    created_at: datetime
    translations: list[TranslationResult]


@dataclass
class ThreadListResult:
    """스레드 목록 결과 DTO"""

    items: list[ThreadResult]
    total: int
    page: int
    limit: int


@dataclass
class CategoryResult:
    """카테고리 결과 DTO"""

    code: str
    name_ko: str
    name_en: str


@dataclass
class CategoriesResult:
    """카테고리 목록 결과 DTO"""

    primary_categories: list[CategoryResult]
    sub_categories: list[CategoryResult]
    mappings: dict[str, list[str]]


# ─────────────────────────────────────────────────
# Thread Use Cases
# ─────────────────────────────────────────────────


class CreateThreadUseCase:
    """스레드 생성 Use Case"""

    def __init__(
        self,
        session: Session,
        category_repository: ICategoryRepository,
        thread_repository: IThreadRepository,
    ) -> None:
        self._session = session
        self._category_repository = category_repository
        self._thread_repository = thread_repository

    def execute(
        self,
        profile_id: UUID,
        primary_category: str,
        sub_category: str,
    ) -> ThreadResult:
        """스레드 생성 실행"""
        # 비즈니스 규칙: 카테고리 조합 유효성 검증
        if not self._category_repository.is_valid_category_mapping(
            primary_category, sub_category
        ):
            raise InvalidCategoryError()

        # Entity 생성
        thread = TranslationThread(
            id=uuid4(),
            profile_id=profile_id,
            primary_category=primary_category,
            sub_category=sub_category,
            created_at=_utcnow(),
        )

        # 저장 및 커밋
        thread = self._thread_repository.create(thread)
        self._session.commit()

        return ThreadResult.from_entity(thread)


class GetThreadUseCase:
    """스레드 상세 조회 Use Case"""

    def __init__(
        self,
        thread_repository: IThreadRepository,
        translation_repository: ITranslationRepository,
    ) -> None:
        self._thread_repository = thread_repository
        self._translation_repository = translation_repository

    def execute(
        self,
        thread_id: UUID,
        profile_id: UUID,
    ) -> ThreadDetailResult:
        """스레드 상세 조회 실행"""
        thread = self._thread_repository.get_by_id(thread_id)

        if thread is None:
            raise ThreadNotFoundError()

        if thread.profile_id != profile_id:
            raise ThreadAccessDeniedError()

        translations, _ = self._translation_repository.get_by_thread_id(thread_id)

        translation_results = [
            TranslationResult(
                id=t.id,
                profile_id=t.profile_id,
                source_text=t.source_text,
                translated_text=t.translated_text,
                source_lang=t.source_lang,
                target_lang=t.target_lang,
                translation_type=t.translation_type,
                mission_progress_id=t.mission_progress_id,
                thread_id=t.thread_id,
                context_primary=t.context_primary,
                context_sub=t.context_sub,
                audio_url=t.audio_url,
                duration_ms=t.duration_ms,
                confidence_score=t.confidence_score,
                created_at=t.created_at,
            )
            for t in translations
        ]

        return ThreadDetailResult(
            id=thread.id,
            profile_id=thread.profile_id,
            primary_category=thread.primary_category,
            sub_category=thread.sub_category,
            created_at=thread.created_at,
            translations=translation_results,
        )


class ListThreadsUseCase:
    """스레드 목록 조회 Use Case"""

    def __init__(self, thread_repository: IThreadRepository) -> None:
        self._thread_repository = thread_repository

    def execute(
        self,
        profile_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> ThreadListResult:
        """스레드 목록 조회 실행"""
        threads, total = self._thread_repository.get_by_profile_id(
            profile_id, page, limit
        )

        items = [ThreadResult.from_entity(t) for t in threads]

        return ThreadListResult(
            items=items,
            total=total,
            page=page,
            limit=limit,
        )


class DeleteThreadUseCase:
    """스레드 삭제 Use Case (Soft Delete)"""

    def __init__(
        self,
        session: Session,
        thread_repository: IThreadRepository,
    ) -> None:
        self._session = session
        self._thread_repository = thread_repository

    def execute(
        self,
        thread_id: UUID,
        profile_id: UUID,
    ) -> None:
        """스레드 삭제 실행"""
        thread = self._thread_repository.get_by_id(thread_id)

        if thread is None:
            raise ThreadNotFoundError()

        if thread.profile_id != profile_id:
            raise ThreadAccessDeniedError()

        self._thread_repository.soft_delete(thread)
        self._session.commit()


# ─────────────────────────────────────────────────
# Category Use Cases
# ─────────────────────────────────────────────────


class GetCategoriesUseCase:
    """카테고리 목록 조회 Use Case"""

    def __init__(self, category_repository: ICategoryRepository) -> None:
        self._category_repository = category_repository

    def execute(self) -> CategoriesResult:
        """카테고리 목록 조회 실행"""
        primaries = self._category_repository.get_primary_categories()
        primary_results = [
            CategoryResult(code=p.code, name_ko=p.name_ko, name_en=p.name_en)
            for p in primaries
        ]

        subs = self._category_repository.get_sub_categories()
        sub_results = [
            CategoryResult(code=s.code, name_ko=s.name_ko, name_en=s.name_en)
            for s in subs
        ]

        mappings_list = self._category_repository.get_category_mappings()
        mappings_dict: dict[str, list[str]] = {}
        for m in mappings_list:
            if m.primary_code not in mappings_dict:
                mappings_dict[m.primary_code] = []
            mappings_dict[m.primary_code].append(m.sub_code)

        return CategoriesResult(
            primary_categories=primary_results,
            sub_categories=sub_results,
            mappings=mappings_dict,
        )


# ─────────────────────────────────────────────────
# Translation Use Cases
# ─────────────────────────────────────────────────


@dataclass
class TextTranslationInput:
    """텍스트 번역 입력 DTO"""

    profile_id: UUID
    source_text: str
    source_lang: str
    target_lang: str
    mission_progress_id: UUID | None = None
    thread_id: UUID | None = None
    context_primary: str | None = None
    context_sub: str | None = None


class CreateTextTranslationUseCase:
    """텍스트 번역 Use Case (Vertex AI Gemini)"""

    def __init__(
        self,
        session: Session,
        translation_repository: ITranslationRepository,
        translation_service: ITranslationService,
        context_service: IContextService,
    ) -> None:
        """Use Case 초기화

        Args:
            session: DB 세션
            translation_repository: 번역 기록 Repository (DIP)
            translation_service: 번역 서비스 (DIP)
            context_service: 컨텍스트 서비스 (DIP)
        """
        self._session = session
        self._translation_repository = translation_repository
        self._translation_service = translation_service
        self._context_service = context_service

    def execute(self, input_data: TextTranslationInput) -> TranslationResult:
        """텍스트 번역 실행"""
        from src.core.enums import TranslationType

        from ._models import Translation

        # 컨텍스트 빌드 (카테고리가 있으면)
        context = None
        if input_data.context_primary and input_data.context_sub:
            context = self._context_service.build_translation_context(
                input_data.context_primary,
                input_data.context_sub,
                input_data.target_lang,
            )

        # 번역 수행
        translated_text = self._translation_service.translate(
            input_data.source_text,
            input_data.source_lang,
            input_data.target_lang,
            context,
        )

        # Entity 생성
        translation = Translation(
            id=uuid4(),
            profile_id=input_data.profile_id,
            source_text=input_data.source_text,
            translated_text=translated_text,
            source_lang=input_data.source_lang,
            target_lang=input_data.target_lang,
            translation_type=TranslationType.TEXT.value,
            mission_progress_id=input_data.mission_progress_id,
            thread_id=input_data.thread_id,
            context_primary=input_data.context_primary,
            context_sub=input_data.context_sub,
            created_at=_utcnow(),
        )

        # 저장 및 커밋
        translation = self._translation_repository.create(translation)
        self._session.commit()

        return TranslationResult(
            id=translation.id,
            profile_id=translation.profile_id,
            source_text=translation.source_text,
            translated_text=translation.translated_text,
            source_lang=translation.source_lang,
            target_lang=translation.target_lang,
            translation_type=translation.translation_type,
            mission_progress_id=translation.mission_progress_id,
            thread_id=translation.thread_id,
            context_primary=translation.context_primary,
            context_sub=translation.context_sub,
            audio_url=translation.audio_url,
            duration_ms=translation.duration_ms,
            confidence_score=translation.confidence_score,
            created_at=translation.created_at,
        )
