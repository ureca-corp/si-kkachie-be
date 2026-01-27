"""translations 도메인 Service"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Session

from src.core.enums import TranslationType
from src.core.exceptions import NotFoundError

from . import repository
from .entities import TextTranslateRequest
from .models import Translation


def _utcnow() -> datetime:
    return datetime.now(UTC)


# 외부 API 함수 (실제 구현은 external 모듈에서)
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Google Cloud Translation API로 텍스트 번역"""
    # TODO: 실제 구현
    # from src.external.translation import get_translation_provider
    # provider = get_translation_provider()
    # return provider.translate(text, source_lang, target_lang)

    # 임시 구현 (테스트용)
    if source_lang == "ko" and target_lang == "en":
        return "Hello"  # 간단한 테스트용
    elif source_lang == "en" and target_lang == "ko":
        return "안녕하세요"
    return text


def speech_to_text(audio_data: bytes, language: str) -> dict:
    """Google Cloud Speech-to-Text API"""
    # TODO: 실제 구현
    return {"text": "안녕하세요", "confidence": 0.95}


def text_to_speech(text: str, language: str) -> dict:
    """Google Cloud Text-to-Speech API"""
    # TODO: 실제 구현
    return {
        "audio_url": "https://storage.supabase.co/tts/abc123.mp3",
        "duration_ms": 1500,
    }


def create_text_translation(
    session: Session,
    profile_id: UUID,
    request: TextTranslateRequest,
) -> Translation:
    """텍스트 번역 생성"""
    # 번역 수행
    translated_text = translate_text(
        request.source_text,
        request.source_lang,
        request.target_lang,
    )

    # 번역 기록 저장
    translation = Translation(
        id=uuid4(),
        profile_id=profile_id,
        source_text=request.source_text,
        translated_text=translated_text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        translation_type=TranslationType.TEXT.value,
        mission_progress_id=(
            UUID(request.mission_progress_id) if request.mission_progress_id else None
        ),
        created_at=_utcnow(),
    )

    return repository.create(session, translation)


def create_voice_translation(
    session: Session,
    profile_id: UUID,
    audio_data: bytes,
    source_lang: str,
    target_lang: str,
    mission_progress_id: str | None = None,
) -> Translation:
    """음성 번역 생성 (STT -> 번역 -> TTS)"""
    # 1. STT
    stt_result = speech_to_text(audio_data, source_lang)
    source_text = stt_result["text"]
    confidence = stt_result["confidence"]

    # 2. 번역
    translated_text = translate_text(source_text, source_lang, target_lang)

    # 3. TTS
    tts_result = text_to_speech(translated_text, target_lang)

    # 번역 기록 저장
    translation = Translation(
        id=uuid4(),
        profile_id=profile_id,
        source_text=source_text,
        translated_text=translated_text,
        source_lang=source_lang,
        target_lang=target_lang,
        translation_type=TranslationType.VOICE.value,
        mission_progress_id=(
            UUID(mission_progress_id) if mission_progress_id else None
        ),
        audio_url=tts_result["audio_url"],
        duration_ms=tts_result["duration_ms"],
        confidence_score=confidence,
        created_at=_utcnow(),
    )

    return repository.create(session, translation)


def get_translations(
    session: Session,
    profile_id: UUID,
    page: int = 1,
    limit: int = 20,
    translation_type: str | None = None,
    mission_progress_id: str | None = None,
) -> tuple[list[Translation], dict]:
    """번역 히스토리 조회"""
    mission_id = UUID(mission_progress_id) if mission_progress_id else None

    translations, total = repository.get_by_profile_id(
        session,
        profile_id,
        page=page,
        limit=limit,
        translation_type=translation_type,
        mission_progress_id=mission_id,
    )

    total_pages = (total + limit - 1) // limit if total > 0 else 0

    pagination = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
    }

    return translations, pagination


def delete_translation(
    session: Session,
    profile_id: UUID,
    translation_id: UUID,
) -> None:
    """번역 기록 삭제 (본인 것만)"""
    translation = repository.get_by_id(session, translation_id)

    if not translation or translation.profile_id != profile_id:
        raise NotFoundError("번역 기록을 찾을 수 없어요")

    repository.delete(session, translation)
