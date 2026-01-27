"""translations 도메인 Controller

SPEC 기반 API:
- POST /translate/text (텍스트 번역)
- POST /translate/voice (음성 번역)
- GET /translations (번역 히스토리 조회)
- DELETE /translations/{id} (번역 기록 삭제)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from . import service
from .entities import TextTranslateRequest, TranslationListResponse, TranslationResponse

router = APIRouter(tags=["translations"])


@router.post("/translate/text", response_model=ApiResponse[TranslationResponse])
def translate_text(
    request: TextTranslateRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[TranslationResponse]:
    """텍스트 번역"""
    translation = service.create_text_translation(session, profile.id, request)

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
        created_at=translation.created_at,
    )

    return ApiResponse(
        status=Status.SUCCESS,
        message="번역이 완료됐어요",
        data=response_data,
    )


@router.post("/translate/voice", response_model=ApiResponse[TranslationResponse])
async def translate_voice(
    profile: CurrentProfile,
    audio_file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...),
    mission_progress_id: str | None = Form(None),
    session: Session = Depends(get_session),
) -> ApiResponse[TranslationResponse] | JSONResponse:
    """음성 번역"""
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

        translation = service.create_voice_translation(
            session,
            profile.id,
            audio_data,
            source_lang,
            target_lang,
            mission_progress_id,
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
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": Status.ERROR_INVALID_AUDIO,
                "message": "잘못된 오디오 파일이에요",
                "data": None,
            },
        )


@router.get("/translations", response_model=ApiResponse[TranslationListResponse])
def get_translations(
    profile: CurrentProfile,
    session: Session = Depends(get_session),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    type: str | None = Query(default=None, alias="type"),
    mission_progress_id: str | None = Query(default=None),
) -> ApiResponse[TranslationListResponse]:
    """번역 히스토리 조회"""
    translations, pagination = service.get_translations(
        session,
        profile.id,
        page=page,
        limit=limit,
        translation_type=type,
        mission_progress_id=mission_progress_id,
    )

    items = [
        TranslationResponse(
            id=str(t.id),
            source_text=t.source_text,
            translated_text=t.translated_text,
            source_lang=t.source_lang,
            target_lang=t.target_lang,
            translation_type=t.translation_type,
            mission_progress_id=(
                str(t.mission_progress_id) if t.mission_progress_id else None
            ),
            audio_url=t.audio_url,
            duration_ms=t.duration_ms,
            confidence_score=t.confidence_score,
            created_at=t.created_at,
        )
        for t in translations
    ]

    return ApiResponse(
        status=Status.SUCCESS,
        message="조회에 성공했어요",
        data=TranslationListResponse(items=items, pagination=pagination),
    )


@router.delete("/translations/{translation_id}", response_model=ApiResponse)
def delete_translation(
    translation_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse:
    """번역 기록 삭제"""
    service.delete_translation(session, profile.id, translation_id)

    return ApiResponse(
        status=Status.SUCCESS,
        message="번역 기록이 삭제됐어요",
    )
