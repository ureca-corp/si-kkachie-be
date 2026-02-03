"""POST /translate/voice 엔드포인트

음성 번역 API (STT → 번역 → TTS 파이프라인)
Controller는 HTTP 처리만 담당, 비즈니스 로직은 Use Case에서 처리
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from ._use_cases import CreateVoiceTranslationUseCase, VoiceTranslationInput

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

        # Use Case 입력 생성
        input_data = VoiceTranslationInput(
            profile_id=profile.id,
            audio_data=audio_data,
            source_lang=source_lang,
            target_lang=target_lang,
            mission_progress_id=(
                UUID(mission_progress_id) if mission_progress_id else None
            ),
            thread_id=UUID(thread_id) if thread_id else None,
            context_primary=context_primary,
            context_sub=context_sub,
        )

        # Use Case 실행
        use_case = CreateVoiceTranslationUseCase(session)
        result = use_case.execute(input_data)

        # 응답 변환
        return ApiResponse(
            status=Status.SUCCESS,
            message="음성 번역이 완료됐어요",
            data=TranslationResponse(
                id=str(result.id),
                source_text=result.source_text,
                translated_text=result.translated_text,
                source_lang=result.source_lang,
                target_lang=result.target_lang,
                translation_type=result.translation_type,
                mission_progress_id=(
                    str(result.mission_progress_id)
                    if result.mission_progress_id
                    else None
                ),
                audio_url=result.audio_url,
                duration_ms=result.duration_ms,
                confidence_score=result.confidence_score,
                created_at=result.created_at,
            ),
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
