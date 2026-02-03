"""translations 도메인 인터페이스

클린 아키텍처: Application Layer에서 사용할 Port 정의
Infrastructure Layer에서 Adapter로 구현
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from ._models import (
        Translation,
        TranslationCategoryMapping,
        TranslationContextPrompt,
        TranslationPrimaryCategory,
        TranslationSubCategory,
        TranslationThread,
    )


# ─────────────────────────────────────────────────
# Service Interfaces
# ─────────────────────────────────────────────────


class ITranslationService(ABC):
    """번역 서비스 인터페이스"""

    @abstractmethod
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """텍스트 번역

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드
            target_lang: 대상 언어 코드
            context: 번역 컨텍스트 (선택)

        Returns:
            번역된 텍스트
        """
        ...


class IContextService(ABC):
    """컨텍스트 서비스 인터페이스"""

    @abstractmethod
    def build_translation_context(
        self,
        primary_code: str | None,
        sub_code: str | None,
        target_lang: str = "ko",
    ) -> str | None:
        """번역용 컨텍스트 빌드

        Args:
            primary_code: 1차 카테고리 코드
            sub_code: 2차 카테고리 코드
            target_lang: 타겟 언어

        Returns:
            컨텍스트 문자열 또는 None
        """
        ...


# ─────────────────────────────────────────────────
# Repository Interfaces
# ─────────────────────────────────────────────────


class ITranslationRepository(ABC):
    """번역 기록 Repository 인터페이스"""

    @abstractmethod
    def create(self, translation: Translation) -> Translation:
        """번역 기록 생성"""
        ...

    @abstractmethod
    def get_by_id(self, translation_id: UUID) -> Translation | None:
        """번역 기록 조회"""
        ...

    @abstractmethod
    def get_by_profile_id(
        self,
        profile_id: UUID,
        page: int = 1,
        limit: int = 20,
        translation_type: str | None = None,
        mission_progress_id: UUID | None = None,
    ) -> tuple[list[Translation], int]:
        """사용자별 번역 히스토리 조회"""
        ...

    @abstractmethod
    def delete(self, translation: Translation) -> None:
        """번역 기록 삭제"""
        ...

    @abstractmethod
    def get_by_thread_id(
        self,
        thread_id: UUID,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[Translation], int]:
        """스레드별 번역 기록 조회"""
        ...


class ICategoryRepository(ABC):
    """카테고리 Repository 인터페이스"""

    @abstractmethod
    def get_primary_categories(
        self,
        active_only: bool = True,
    ) -> list[TranslationPrimaryCategory]:
        """1차 카테고리 목록 조회"""
        ...

    @abstractmethod
    def get_sub_categories(
        self,
        active_only: bool = True,
    ) -> list[TranslationSubCategory]:
        """2차 카테고리 목록 조회"""
        ...

    @abstractmethod
    def get_category_mappings(self) -> list[TranslationCategoryMapping]:
        """카테고리 매핑 목록 조회"""
        ...

    @abstractmethod
    def get_context_prompt(
        self,
        primary_code: str,
        sub_code: str,
    ) -> TranslationContextPrompt | None:
        """컨텍스트 프롬프트 조회"""
        ...

    @abstractmethod
    def is_valid_category_mapping(
        self,
        primary_code: str,
        sub_code: str,
    ) -> bool:
        """카테고리 조합 유효성 확인"""
        ...


class IThreadRepository(ABC):
    """스레드 Repository 인터페이스"""

    @abstractmethod
    def create(self, thread: TranslationThread) -> TranslationThread:
        """스레드 생성"""
        ...

    @abstractmethod
    def get_by_id(self, thread_id: UUID) -> TranslationThread | None:
        """스레드 조회"""
        ...

    @abstractmethod
    def get_by_profile_id(
        self,
        profile_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[TranslationThread], int]:
        """사용자별 스레드 목록 조회"""
        ...

    @abstractmethod
    def soft_delete(self, thread: TranslationThread) -> TranslationThread:
        """스레드 소프트 삭제"""
        ...
