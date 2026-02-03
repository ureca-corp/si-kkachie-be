"""translations 도메인 Use Cases

클린 아키텍처: Application Layer
- 비즈니스 로직을 캡슐화
- Controller에서 분리하여 재사용성 및 테스트 용이성 확보
- Repository를 통해 데이터 접근 (의존성 주입)
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Session

from . import _repository
from ._exceptions import (
    InvalidCategoryError,
    ThreadAccessDeniedError,
    ThreadNotFoundError,
)
from ._models import TranslationThread


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
    def from_entity(cls, thread: TranslationThread) -> "ThreadResult":
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
# Use Cases
# ─────────────────────────────────────────────────


class CreateThreadUseCase:
    """스레드 생성 Use Case

    비즈니스 규칙:
    - 카테고리 조합이 유효해야 함 (매핑 테이블에 존재)
    """

    def __init__(self, session: Session):
        self._session = session

    def execute(
        self,
        profile_id: UUID,
        primary_category: str,
        sub_category: str,
    ) -> ThreadResult:
        """스레드 생성 실행

        Args:
            profile_id: 프로필 ID
            primary_category: 1차 카테고리 코드
            sub_category: 2차 카테고리 코드

        Returns:
            생성된 스레드 정보

        Raises:
            InvalidCategoryError: 유효하지 않은 카테고리 조합
        """
        # 비즈니스 규칙: 카테고리 조합 유효성 검증
        if not _repository.is_valid_category_mapping(
            self._session, primary_category, sub_category
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

        # 저장
        thread = _repository.create_thread(self._session, thread)

        return ThreadResult.from_entity(thread)


class GetThreadUseCase:
    """스레드 상세 조회 Use Case

    비즈니스 규칙:
    - 스레드가 존재해야 함
    - 요청자가 스레드 소유자여야 함
    """

    def __init__(self, session: Session):
        self._session = session

    def execute(
        self,
        thread_id: UUID,
        profile_id: UUID,
    ) -> ThreadDetailResult:
        """스레드 상세 조회 실행

        Args:
            thread_id: 스레드 ID
            profile_id: 요청자 프로필 ID

        Returns:
            스레드 상세 정보 (번역 기록 포함)

        Raises:
            ThreadNotFoundError: 스레드가 존재하지 않음
            ThreadAccessDeniedError: 접근 권한 없음
        """
        # 스레드 조회
        thread = _repository.get_thread_by_id(self._session, thread_id)

        if thread is None:
            raise ThreadNotFoundError()

        # 소유권 확인
        if thread.profile_id != profile_id:
            raise ThreadAccessDeniedError()

        # 번역 기록 조회
        translations, _ = _repository.get_translations_by_thread_id(
            self._session, thread_id
        )

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

    def __init__(self, session: Session):
        self._session = session

    def execute(
        self,
        profile_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> ThreadListResult:
        """스레드 목록 조회 실행

        Args:
            profile_id: 프로필 ID
            page: 페이지 번호 (1부터 시작)
            limit: 페이지당 항목 수

        Returns:
            스레드 목록 및 페이지네이션 정보
        """
        threads, total = _repository.get_threads_by_profile_id(
            self._session, profile_id, page, limit
        )

        items = [ThreadResult.from_entity(t) for t in threads]

        return ThreadListResult(
            items=items,
            total=total,
            page=page,
            limit=limit,
        )


class DeleteThreadUseCase:
    """스레드 삭제 Use Case (Soft Delete)

    비즈니스 규칙:
    - 스레드가 존재해야 함
    - 요청자가 스레드 소유자여야 함
    """

    def __init__(self, session: Session):
        self._session = session

    def execute(
        self,
        thread_id: UUID,
        profile_id: UUID,
    ) -> None:
        """스레드 삭제 실행

        Args:
            thread_id: 스레드 ID
            profile_id: 요청자 프로필 ID

        Raises:
            ThreadNotFoundError: 스레드가 존재하지 않음
            ThreadAccessDeniedError: 접근 권한 없음
        """
        # 스레드 조회
        thread = _repository.get_thread_by_id(self._session, thread_id)

        if thread is None:
            raise ThreadNotFoundError()

        # 소유권 확인
        if thread.profile_id != profile_id:
            raise ThreadAccessDeniedError()

        # Soft delete
        _repository.soft_delete_thread(self._session, thread)


class GetCategoriesUseCase:
    """카테고리 목록 조회 Use Case"""

    def __init__(self, session: Session):
        self._session = session

    def execute(self) -> CategoriesResult:
        """카테고리 목록 조회 실행

        Returns:
            1차/2차 카테고리 목록 및 매핑 정보
        """
        # 1차 카테고리 조회
        primaries = _repository.get_primary_categories(self._session)
        primary_results = [
            CategoryResult(code=p.code, name_ko=p.name_ko, name_en=p.name_en)
            for p in primaries
        ]

        # 2차 카테고리 조회
        subs = _repository.get_sub_categories(self._session)
        sub_results = [
            CategoryResult(code=s.code, name_ko=s.name_ko, name_en=s.name_en)
            for s in subs
        ]

        # 매핑 조회 및 변환
        mappings_list = _repository.get_category_mappings(self._session)
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


@dataclass
class VoiceTranslationInput:
    """음성 번역 입력 DTO"""

    profile_id: UUID
    audio_data: bytes
    source_lang: str
    target_lang: str
    mission_progress_id: UUID | None = None
    thread_id: UUID | None = None
    context_primary: str | None = None
    context_sub: str | None = None


class CreateTextTranslationUseCase:
    """텍스트 번역 Use Case

    비즈니스 로직:
    - 컨텍스트가 있으면 Vertex AI (Gemini) 사용
    - 컨텍스트가 없으면 Google Translation API 사용
    """

    def __init__(self, session: Session):
        self._session = session

    def execute(self, input_data: TextTranslationInput) -> TranslationResult:
        """텍스트 번역 실행

        Args:
            input_data: 번역 입력 데이터

        Returns:
            번역 결과 DTO
        """
        from src.core.enums import TranslationType

        from . import _context_service, _translation_service
        from ._models import Translation

        # 컨텍스트 빌드 (카테고리가 있으면)
        context = None
        if input_data.context_primary and input_data.context_sub:
            context = _context_service.build_translation_context(
                self._session,
                input_data.context_primary,
                input_data.context_sub,
                input_data.target_lang,
            )

        # 번역 수행
        translated_text = _translation_service.translate(
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

        # 저장
        translation = _repository.create(self._session, translation)

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


class CreateVoiceTranslationUseCase:
    """음성 번역 Use Case

    비즈니스 로직:
    - STT → 번역 → TTS 파이프라인
    - 컨텍스트가 있으면 Vertex AI (Gemini) 사용
    """

    def __init__(self, session: Session):
        self._session = session

    def execute(self, input_data: VoiceTranslationInput) -> TranslationResult:
        """음성 번역 실행

        Args:
            input_data: 번역 입력 데이터

        Returns:
            번역 결과 DTO
        """
        from src.core.enums import TranslationType

        from . import _context_service, _translation_service
        from ._models import Translation

        # 1. STT (Speech-to-Text)
        stt_result = _translation_service.speech_to_text(
            input_data.audio_data, input_data.source_lang
        )
        source_text = stt_result["text"]
        confidence = stt_result["confidence"]

        # 2. 컨텍스트 빌드 (카테고리가 있으면)
        context = None
        if input_data.context_primary and input_data.context_sub:
            context = _context_service.build_translation_context(
                self._session,
                input_data.context_primary,
                input_data.context_sub,
                input_data.target_lang,
            )

        # 3. 번역 (컨텍스트가 있으면 Vertex AI 사용)
        translated_text = _translation_service.translate(
            source_text,
            input_data.source_lang,
            input_data.target_lang,
            context,
        )

        # 4. TTS (Text-to-Speech)
        tts_result = _translation_service.text_to_speech(
            translated_text, input_data.target_lang
        )

        # Entity 생성
        translation = Translation(
            id=uuid4(),
            profile_id=input_data.profile_id,
            source_text=source_text,
            translated_text=translated_text,
            source_lang=input_data.source_lang,
            target_lang=input_data.target_lang,
            translation_type=TranslationType.VOICE.value,
            mission_progress_id=input_data.mission_progress_id,
            thread_id=input_data.thread_id,
            context_primary=input_data.context_primary,
            context_sub=input_data.context_sub,
            audio_url=tts_result["audio_url"],
            duration_ms=tts_result["duration_ms"],
            confidence_score=confidence,
            created_at=_utcnow(),
        )

        # 저장
        translation = _repository.create(self._session, translation)

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
