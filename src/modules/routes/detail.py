"""경로 상세 조회

GET /routes/{route_id}
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.exceptions import NotFoundError
from src.core.response import ApiResponse, Status

from . import _repository
from ._utils import format_distance, format_duration
from .search import PointResponse, RouteSearchResponse

# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────


def get_route_detail(
    session: Session,
    profile_id: UUID,
    route_id: UUID,
) -> RouteSearchResponse:
    """경로 상세 조회"""
    route = _repository.get_by_id(session, route_id, profile_id)
    if route is None:
        raise NotFoundError("경로 기록을 찾을 수 없어요")

    return RouteSearchResponse(
        id=str(route.id),
        start=PointResponse(
            name=route.start_name,
            lat=route.start_lat,
            lng=route.start_lng,
        ),
        end=PointResponse(
            name=route.end_name,
            lat=route.end_lat,
            lng=route.end_lng,
        ),
        total_distance_m=route.total_distance_m,
        total_duration_s=route.total_duration_s,
        distance_text=format_distance(route.total_distance_m),
        duration_text=format_duration(route.total_duration_s),
        path=route.path_data,
    )


# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()


@router.get("/{route_id}", response_model=ApiResponse[RouteSearchResponse])
def get_route_detail_endpoint(
    route_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[RouteSearchResponse]:
    """경로 상세 조회"""
    result = get_route_detail(session, profile.id, route_id)

    return ApiResponse(
        status=Status.SUCCESS,
        message="경로 조회에 성공했어요",
        data=result,
    )
