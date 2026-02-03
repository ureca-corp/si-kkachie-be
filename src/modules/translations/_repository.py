"""translations 도메인 Repository (공유)"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Session, func, select

from ._models import Translation

if TYPE_CHECKING:
    from ._models import (
        TranslationCategoryMapping,
        TranslationContextPrompt,
        TranslationPrimaryCategory,
        TranslationSubCategory,
        TranslationThread,
    )


def _utcnow() -> datetime:
    return datetime.now(UTC)


def create(session: Session, translation: Translation) -> Translation:
    """번역 기록 생성"""
    session.add(translation)
    session.commit()
    session.refresh(translation)
    return translation


def get_by_id(session: Session, translation_id: UUID) -> Translation | None:
    """번역 기록 조회"""
    return session.get(Translation, translation_id)


def get_by_profile_id(
    session: Session,
    profile_id: UUID,
    page: int = 1,
    limit: int = 20,
    translation_type: str | None = None,
    mission_progress_id: UUID | None = None,
) -> tuple[list[Translation], int]:
    """사용자별 번역 히스토리 조회 (페이지네이션)"""
    # 기본 쿼리
    query = select(Translation).where(Translation.profile_id == profile_id)

    # 필터 적용
    if translation_type:
        query = query.where(Translation.translation_type == translation_type)
    if mission_progress_id:
        query = query.where(Translation.mission_progress_id == mission_progress_id)

    # 전체 개수 조회
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # 정렬 및 페이지네이션
    query = query.order_by(Translation.created_at.desc())  # type: ignore[union-attr]
    query = query.offset((page - 1) * limit).limit(limit)

    translations = list(session.exec(query).all())
    return translations, total


def delete(session: Session, translation: Translation) -> None:
    """번역 기록 삭제"""
    session.delete(translation)
    session.commit()


# ─────────────────────────────────────────────────
# Category Repository Functions
# ─────────────────────────────────────────────────


def get_primary_categories(
    session: Session,
    active_only: bool = True,
) -> list[TranslationPrimaryCategory]:
    """1차 카테고리 목록 조회"""
    from ._models import TranslationPrimaryCategory

    query = select(TranslationPrimaryCategory)
    if active_only:
        query = query.where(TranslationPrimaryCategory.is_active == True)  # noqa: E712
    query = query.order_by(TranslationPrimaryCategory.display_order)
    return list(session.exec(query).all())


def get_sub_categories(
    session: Session,
    active_only: bool = True,
) -> list[TranslationSubCategory]:
    """2차 카테고리 목록 조회"""
    from ._models import TranslationSubCategory

    query = select(TranslationSubCategory)
    if active_only:
        query = query.where(TranslationSubCategory.is_active == True)  # noqa: E712
    query = query.order_by(TranslationSubCategory.display_order)
    return list(session.exec(query).all())


def get_category_mappings(
    session: Session,
) -> list[TranslationCategoryMapping]:
    """카테고리 매핑 목록 조회"""
    from ._models import TranslationCategoryMapping

    query = select(TranslationCategoryMapping)
    return list(session.exec(query).all())


def get_context_prompt(
    session: Session,
    primary_code: str,
    sub_code: str,
) -> TranslationContextPrompt | None:
    """컨텍스트 프롬프트 조회"""
    from ._models import TranslationContextPrompt

    query = (
        select(TranslationContextPrompt)
        .where(TranslationContextPrompt.primary_code == primary_code)
        .where(TranslationContextPrompt.sub_code == sub_code)
        .where(TranslationContextPrompt.is_active == True)  # noqa: E712
    )
    return session.exec(query).first()


# ─────────────────────────────────────────────────
# Thread Repository Functions
# ─────────────────────────────────────────────────


def create_thread(
    session: Session,
    thread: TranslationThread,
) -> TranslationThread:
    """번역 스레드 생성"""
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread


def get_thread_by_id(
    session: Session,
    thread_id: UUID,
) -> TranslationThread | None:
    """번역 스레드 조회"""
    from ._models import TranslationThread

    thread = session.get(TranslationThread, thread_id)
    if thread and thread.deleted_at is not None:
        return None
    return thread


def get_threads_by_profile_id(
    session: Session,
    profile_id: UUID,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[TranslationThread], int]:
    """사용자별 스레드 목록 조회 (페이지네이션)"""
    from ._models import TranslationThread

    # 기본 쿼리 (soft delete 제외)
    query = (
        select(TranslationThread)
        .where(TranslationThread.profile_id == profile_id)
        .where(TranslationThread.deleted_at == None)  # noqa: E711
    )

    # 전체 개수 조회
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # 정렬 및 페이지네이션 (최신순)
    query = query.order_by(TranslationThread.created_at.desc())  # type: ignore[union-attr]
    query = query.offset((page - 1) * limit).limit(limit)

    threads = list(session.exec(query).all())
    return threads, total


def soft_delete_thread(
    session: Session,
    thread: TranslationThread,
) -> TranslationThread:
    """번역 스레드 소프트 삭제"""
    thread.deleted_at = _utcnow()
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread


def get_translations_by_thread_id(
    session: Session,
    thread_id: UUID,
    page: int = 1,
    limit: int = 50,
) -> tuple[list[Translation], int]:
    """스레드별 번역 기록 조회"""
    query = select(Translation).where(Translation.thread_id == thread_id)

    # 전체 개수 조회
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # 정렬 및 페이지네이션 (오래된 순 - 대화 흐름)
    query = query.order_by(Translation.created_at.asc())  # type: ignore[union-attr]
    query = query.offset((page - 1) * limit).limit(limit)

    translations = list(session.exec(query).all())
    return translations, total


def is_valid_category_mapping(
    session: Session,
    primary_code: str,
    sub_code: str,
) -> bool:
    """카테고리 조합이 유효한지 확인"""
    from ._models import TranslationCategoryMapping

    query = (
        select(TranslationCategoryMapping)
        .where(TranslationCategoryMapping.primary_code == primary_code)
        .where(TranslationCategoryMapping.sub_code == sub_code)
    )
    return session.exec(query).first() is not None
