"""POST /translate/text 엔드포인트

텍스트 번역 기능을 담당하는 Vertical Slice
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, model_validator
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.enums import TranslationType
from src.core.response import ApiResponse, Status

from . import _repository, _translation_service
from ._models import Translation

router = APIRouter(tags=["translations"])


# ─────────────────────────────────────────────────
# Request/Response DTOs
# ─────────────────────────────────────────────────


class TextTranslateRequest(BaseModel):
    """텍스트 번역 요청"""

    source_text: str = Field(min_length=1, max_length=5000)
    source_lang: str = Field(pattern=r"^(ko|en)$")
    target_lang: str = Field(pattern=r"^(ko|en)$")
    mission_progress_id: str | None = None

    @model_validator(mode="after")
    def validate_different_languages(self):
        if self.source_lang == self.target_lang:
            msg = "같은 언어로는 번역할 수 없어요"
            raise ValueError(msg)
        return self


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


def create_text_translation(
    session: Session,
    profile_id: UUID,
    request: TextTranslateRequest,
) -> Translation:
    """텍스트 번역 생성"""
    # 번역 수행
    translated_text = _translation_service.translate(
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

    return _repository.create(session, translation)


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.post("/translate/text", response_model=ApiResponse[TranslationResponse])
def translate_text(
    request: TextTranslateRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[TranslationResponse]:
    """텍스트 번역"""
    translation = create_text_translation(session, profile.id, request)

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
