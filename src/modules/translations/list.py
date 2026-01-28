"""GET /translations 엔드포인트

번역 히스토리 조회 기능을 담당하는 Vertical Slice
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from . import _repository
from ._models import Translation

router = APIRouter(tags=["translations"])


# ─────────────────────────────────────────────────
# Response DTOs
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


class TranslationListResponse(BaseModel):
    """번역 목록 응답"""

    items: list[TranslationResponse]
    pagination: dict


# ─────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────


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

    translations, total = _repository.get_by_profile_id(
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


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.get("/translations", response_model=ApiResponse[TranslationListResponse])
def list_translations(
    profile: CurrentProfile,
    session: Session = Depends(get_session),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    type: str | None = Query(default=None, alias="type"),
    mission_progress_id: str | None = Query(default=None),
) -> ApiResponse[TranslationListResponse]:
    """번역 히스토리 조회"""
    translations, pagination = get_translations(
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
