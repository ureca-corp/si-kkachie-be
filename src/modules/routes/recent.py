"""최근 경로 조회

GET /routes/recent
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
from ._models import RouteHistory

# ─────────────────────────────────────────────────
# Response DTO
# ─────────────────────────────────────────────────


class RouteHistoryResponse(BaseModel):
    """경로 히스토리 응답"""

    id: str
    start_name: str
    end_name: str
    total_distance_m: int
    total_duration_s: int
    created_at: datetime


# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────


def get_recent_routes(
    session: Session,
    profile_id: UUID,
    limit: int = 10,
) -> list[RouteHistory]:
    """최근 경로 조회"""
    # 최대 50개 제한
    limit = min(limit, 50)
    return _repository.get_by_profile_id(session, profile_id, limit)


# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()


@router.get("/recent", response_model=ApiResponse[list[RouteHistoryResponse]])
def get_recent_routes_endpoint(
    profile: CurrentProfile,
    session: Session = Depends(get_session),
    limit: int = Query(default=10, ge=1, le=50),
) -> ApiResponse[list[RouteHistoryResponse]]:
    """최근 경로 조회"""
    routes = get_recent_routes(session, profile.id, limit)

    items = [
        RouteHistoryResponse(
            id=str(r.id),
            start_name=r.start_name,
            end_name=r.end_name,
            total_distance_m=r.total_distance_m,
            total_duration_s=r.total_duration_s,
            created_at=r.created_at,
        )
        for r in routes
    ]

    return ApiResponse(
        status=Status.SUCCESS,
        message="조회에 성공했어요",
        data=items,
    )
