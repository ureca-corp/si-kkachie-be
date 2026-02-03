"""POST /translate/voice 엔드포인트

음성 번역 기능을 담당하는 Vertical Slice
STT -> 번역 -> TTS 파이프라인 처리
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.enums import TranslationType
from src.core.response import ApiResponse, Status

from . import _repository, _translation_service
from ._models import Translation

router = APIRouter(tags=["translations"])


# ─────────────────────────────────────────────────
# Response DTO
# ─────────────────────────────────────────────────


class TranslationResponse(BaseModel):
    """번역 응답"""

    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    translation_type: str
    mission_progress_id: str | None = None
    audio_url: str | None = None
    duration_ms: int | None = None
    confidence_score: float | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────


def _utcnow() -> datetime:
    return datetime.now(UTC)


def create_voice_translation(
    session: Session,
    profile_id: UUID,
    audio_data: bytes,
    source_lang: str,
    target_lang: str,
    mission_progress_id: str | None = None,
    thread_id: str | None = None,
    context_primary: str | None = None,
    context_sub: str | None = None,
) -> Translation:
    """음성 번역 생성 (STT -> 번역 -> TTS)

    Args:
        session: DB 세션
        profile_id: 프로필 ID
        audio_data: 오디오 바이너리 데이터
        source_lang: 원본 언어
        target_lang: 번역 언어
        mission_progress_id: 미션 진행 ID (선택)
        thread_id: 스레드 ID (선택)
        context_primary: 1차 카테고리 코드 (선택)
        context_sub: 2차 카테고리 코드 (선택)
    """
    # 1. STT
    stt_result = _translation_service.speech_to_text(audio_data, source_lang)
    source_text = stt_result["text"]
    confidence = stt_result["confidence"]

    # 2. 번역 (컨텍스트가 있으면 적용)
    # TODO: 컨텍스트 프롬프트를 번역 서비스에 전달 (향후 구현)
    translated_text = _translation_service.translate(
        source_text, source_lang, target_lang
    )

    # 3. TTS
    tts_result = _translation_service.text_to_speech(translated_text, target_lang)

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
        thread_id=UUID(thread_id) if thread_id else None,
        context_primary=context_primary,
        context_sub=context_sub,
    )

    return _repository.create(session, translation)


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.post("/translate/voice", response_model=ApiResponse[TranslationResponse])
async def translate_voice(
    profile: CurrentProfile,
    audio_file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...),
    mission_progress_id: str | None = Form(None),
    thread_id: str | None = Form(None),
    context_primary: str | None = Form(None),
    context_sub: str | None = Form(None),
    session: Session = Depends(get_session),
) -> ApiResponse[TranslationResponse] | JSONResponse:
    """음성 번역

    Args:
        audio_file: 오디오 파일
        source_lang: 원본 언어
        target_lang: 번역 언어
        mission_progress_id: 미션 진행 ID (선택)
        thread_id: 번역 스레드 ID (선택)
        context_primary: 1차 카테고리 코드 (선택, 예: FD6)
        context_sub: 2차 카테고리 코드 (선택, 예: ordering)
    """
    # 언어 검증
    if source_lang == target_lang:
        return JSONResponse(
            status_code=422,
            content={
                "status": Status.VALIDATION_FAILED,
                "message": "같은 언어로는 번역할 수 없어요",
                "data": None,
            },
        )

    try:
        audio_data = await audio_file.read()

        translation = create_voice_translation(
            session,
            profile.id,
            audio_data,
            source_lang,
            target_lang,
            mission_progress_id,
            thread_id,
            context_primary,
            context_sub,
        )

        response_data = TranslationResponse(
            id=str(translation.id),
            source_text=translation.source_text,
            translated_text=translation.translated_text,
            source_lang=translation.source_lang,
            target_lang=translation.target_lang,
            translation_type=translation.translation_type,
            mission_progress_id=(
                str(translation.mission_progress_id)
                if translation.mission_progress_id
                else None
            ),
            audio_url=translation.audio_url,
            duration_ms=translation.duration_ms,
            confidence_score=translation.confidence_score,
            created_at=translation.created_at,
        )

        return ApiResponse(
            status=Status.SUCCESS,
            message="음성 번역이 완료됐어요",
            data=response_data,
        )
    except (OSError, ValueError):
        # 오디오 파일 검증 실패만 처리, 다른 예외는 전역 핸들러로 전파
        return JSONResponse(
            status_code=400,
            content={
                "status": Status.ERROR_INVALID_AUDIO,
                "message": "잘못된 오디오 파일이에요",
                "data": None,
            },
        )
