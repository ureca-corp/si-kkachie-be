"""phrases 도메인 Controller

SPEC 기반 API:
- GET /phrases (추천 문장 목록)
- POST /phrases/{id}/use (문장 사용 기록)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from . import service
from .entities import PhraseResponse, PhraseUseResponse

router = APIRouter(prefix="/phrases", tags=["phrases"])


@router.get("", response_model=ApiResponse[list[PhraseResponse]])
def list_phrases(
    profile: CurrentProfile,
    session: Session = Depends(get_session),
    category: str | None = Query(default=None),
    mission_step_id: str | None = Query(default=None),
) -> ApiResponse[list[PhraseResponse]]:
    """추천 문장 목록 조회"""
    step_id = UUID(mission_step_id) if mission_step_id else None

    phrases = service.get_phrases(session, category=category, mission_step_id=step_id)

    items = [
        PhraseResponse(
            id=str(p.id),
            text_ko=p.text_ko,
            text_en=p.text_en,
            category=p.category,
            usage_count=p.usage_count,
        )
        for p in phrases
    ]

    return ApiResponse(
        status=Status.SUCCESS,
        message="조회에 성공했어요",
        data=items,
    )


@router.post("/{phrase_id}/use", response_model=ApiResponse[PhraseUseResponse])
def use_phrase(
    phrase_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[PhraseUseResponse] | JSONResponse:
    """문장 사용 기록"""
    try:
        phrase = service.use_phrase(session, phrase_id)

        return ApiResponse(
            status=Status.SUCCESS,
            message="사용이 기록됐어요",
            data=PhraseUseResponse(
                id=str(phrase.id),
                usage_count=phrase.usage_count,
            ),
        )
    except Exception:
        return JSONResponse(
            status_code=404,
            content={
                "status": Status.PHRASE_NOT_FOUND,
                "message": "문장을 찾을 수 없어요",
                "data": None,
            },
        )
