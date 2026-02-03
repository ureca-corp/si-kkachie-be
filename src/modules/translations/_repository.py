"""translations 도메인 Repository 구현

클린 아키텍처: Infrastructure Layer
- 인터페이스를 구현하여 데이터 접근 추상화
- Session을 생성자에서 주입받아 사용
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, func, select

from ._interfaces import ICategoryRepository, IThreadRepository, ITranslationRepository
from ._models import (
    Translation,
    TranslationCategoryMapping,
    TranslationContextPrompt,
    TranslationPrimaryCategory,
    TranslationSubCategory,
    TranslationThread,
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ─────────────────────────────────────────────────
# Translation Repository
# ─────────────────────────────────────────────────


class TranslationRepository(ITranslationRepository):
    """번역 기록 Repository 구현"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, translation: Translation) -> Translation:
        """번역 기록 생성 (commit은 Use Case에서 수행)"""
        self._session.add(translation)
        self._session.flush()
        return translation

    def get_by_id(self, translation_id: UUID) -> Translation | None:
        """번역 기록 조회"""
        return self._session.get(Translation, translation_id)

    def get_by_profile_id(
        self,
        profile_id: UUID,
        page: int = 1,
        limit: int = 20,
        translation_type: str | None = None,
        mission_progress_id: UUID | None = None,
    ) -> tuple[list[Translation], int]:
        """사용자별 번역 히스토리 조회 (페이지네이션)"""
        query = select(Translation).where(Translation.profile_id == profile_id)

        if translation_type:
            query = query.where(Translation.translation_type == translation_type)
        if mission_progress_id:
            query = query.where(Translation.mission_progress_id == mission_progress_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = self._session.exec(count_query).one()

        query = query.order_by(Translation.created_at.desc())  # type: ignore[union-attr]
        query = query.offset((page - 1) * limit).limit(limit)

        translations = list(self._session.exec(query).all())
        return translations, total

    def delete(self, translation: Translation) -> None:
        """번역 기록 삭제 (commit은 Use Case에서 수행)"""
        self._session.delete(translation)
        self._session.flush()

    def get_by_thread_id(
        self,
        thread_id: UUID,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[Translation], int]:
        """스레드별 번역 기록 조회"""
        query = select(Translation).where(Translation.thread_id == thread_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = self._session.exec(count_query).one()

        query = query.order_by(Translation.created_at.asc())  # type: ignore[union-attr]
        query = query.offset((page - 1) * limit).limit(limit)

        translations = list(self._session.exec(query).all())
        return translations, total


# ─────────────────────────────────────────────────
# Category Repository
# ─────────────────────────────────────────────────


class CategoryRepository(ICategoryRepository):
    """카테고리 Repository 구현"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_primary_categories(
        self,
        active_only: bool = True,
    ) -> list[TranslationPrimaryCategory]:
        """1차 카테고리 목록 조회"""
        query = select(TranslationPrimaryCategory)
        if active_only:
            query = query.where(TranslationPrimaryCategory.is_active == True)  # noqa: E712
        query = query.order_by(TranslationPrimaryCategory.display_order)
        return list(self._session.exec(query).all())

    def get_sub_categories(
        self,
        active_only: bool = True,
    ) -> list[TranslationSubCategory]:
        """2차 카테고리 목록 조회"""
        query = select(TranslationSubCategory)
        if active_only:
            query = query.where(TranslationSubCategory.is_active == True)  # noqa: E712
        query = query.order_by(TranslationSubCategory.display_order)
        return list(self._session.exec(query).all())

    def get_category_mappings(self) -> list[TranslationCategoryMapping]:
        """카테고리 매핑 목록 조회"""
        query = select(TranslationCategoryMapping)
        return list(self._session.exec(query).all())

    def get_context_prompt(
        self,
        primary_code: str,
        sub_code: str,
    ) -> TranslationContextPrompt | None:
        """컨텍스트 프롬프트 조회"""
        query = (
            select(TranslationContextPrompt)
            .where(TranslationContextPrompt.primary_code == primary_code)
            .where(TranslationContextPrompt.sub_code == sub_code)
            .where(TranslationContextPrompt.is_active == True)  # noqa: E712
        )
        return self._session.exec(query).first()

    def is_valid_category_mapping(
        self,
        primary_code: str,
        sub_code: str,
    ) -> bool:
        """카테고리 조합이 유효한지 확인"""
        query = (
            select(TranslationCategoryMapping)
            .where(TranslationCategoryMapping.primary_code == primary_code)
            .where(TranslationCategoryMapping.sub_code == sub_code)
        )
        return self._session.exec(query).first() is not None


# ─────────────────────────────────────────────────
# Thread Repository
# ─────────────────────────────────────────────────


class ThreadRepository(IThreadRepository):
    """스레드 Repository 구현"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, thread: TranslationThread) -> TranslationThread:
        """스레드 생성 (commit은 Use Case에서 수행)"""
        self._session.add(thread)
        self._session.flush()
        return thread

    def get_by_id(self, thread_id: UUID) -> TranslationThread | None:
        """스레드 조회 (soft delete된 것 제외)"""
        thread = self._session.get(TranslationThread, thread_id)
        if thread and thread.deleted_at is not None:
            return None
        return thread

    def get_by_profile_id(
        self,
        profile_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[TranslationThread], int]:
        """사용자별 스레드 목록 조회 (페이지네이션)"""
        query = (
            select(TranslationThread)
            .where(TranslationThread.profile_id == profile_id)
            .where(TranslationThread.deleted_at == None)  # noqa: E711
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = self._session.exec(count_query).one()

        query = query.order_by(TranslationThread.created_at.desc())  # type: ignore[union-attr]
        query = query.offset((page - 1) * limit).limit(limit)

        threads = list(self._session.exec(query).all())
        return threads, total

    def soft_delete(self, thread: TranslationThread) -> TranslationThread:
        """스레드 소프트 삭제 (commit은 Use Case에서 수행)"""
        thread.deleted_at = _utcnow()
        self._session.add(thread)
        self._session.flush()
        return thread
