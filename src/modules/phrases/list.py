"""GET /phrases - 추천 문장 목록 조회

Vertical Slice: 하나의 엔드포인트에 필요한 모든 코드를 포함
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from . import _repository as repository

router = APIRouter()


# === Response DTO ===
class PhraseResponse(BaseModel):
    """추천 문장 응답"""

    id: str
    text_ko: str
    text_en: str
    category: str
    usage_count: int

    model_config = {"from_attributes": True}


# === Endpoint ===
@router.get("/", response_model=ApiResponse[list[PhraseResponse]])
def list_phrases(
    profile: CurrentProfile,
    session: Session = Depends(get_session),
    category: str | None = Query(default=None),
    mission_step_id: str | None = Query(default=None),
) -> ApiResponse[list[PhraseResponse]]:
    """추천 문장 목록 조회

    Query Params:
    - category: 카테고리별 필터
    - mission_step_id: 미션 단계별 필터
    """
    # 필터링 로직
    if mission_step_id:
        step_id = UUID(mission_step_id)
        phrases = repository.get_by_mission_step_id(session, step_id)
    elif category:
        phrases = repository.get_by_category(session, category)
    else:
        phrases = repository.get_all_active(session)

    # Response 변환
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
