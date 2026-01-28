"""경로 검색

POST /routes/search
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.exceptions import ExternalServiceError
from src.core.response import ApiResponse, Status

from . import _repository
from ._models import RouteHistory, make_point
from ._utils import format_distance, format_duration

# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────


class PointRequest(BaseModel):
    """좌표 요청"""

    name: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class RouteSearchRequest(BaseModel):
    """경로 검색 요청"""

    start: PointRequest
    end: PointRequest
    waypoints: list[PointRequest] | None = Field(default=None, max_length=5)
    option: str = "traoptimal"

    @field_validator("waypoints")
    @classmethod
    def validate_waypoints(cls, v: list | None) -> list | None:
        if v and len(v) > 5:
            msg = "경유지는 최대 5개까지 가능해요"
            raise ValueError(msg)
        return v


class PointResponse(BaseModel):
    """좌표 응답"""

    name: str
    lat: float
    lng: float


class RouteSearchResponse(BaseModel):
    """경로 검색 응답"""

    id: str
    start: PointResponse
    end: PointResponse
    total_distance_m: int
    total_duration_s: int
    distance_text: str
    duration_text: str
    path: list[dict]


# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────


def _utcnow() -> datetime:
    return datetime.now(UTC)


def search_route_from_naver(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    waypoints: list[dict] | None = None,
    option: str = "traoptimal",
) -> dict:
    """Naver Maps Directions API 호출

    TODO: 실제 구현
    """
    # 임시 구현 (테스트용)
    return {
        "total_distance_m": 12500,
        "total_duration_s": 1800,
        "path": [
            {"lat": start_lat, "lng": start_lng},
            {"lat": end_lat, "lng": end_lng},
        ],
    }


def search_route(
    session: Session,
    profile_id: UUID,
    request: RouteSearchRequest,
) -> RouteSearchResponse:
    """경로 검색 및 저장"""
    waypoints_data = None
    if request.waypoints:
        waypoints_data = [
            {"name": wp.name, "lat": wp.lat, "lng": wp.lng} for wp in request.waypoints
        ]

    try:
        # Naver API 호출
        route_data = search_route_from_naver(
            start_lat=request.start.lat,
            start_lng=request.start.lng,
            end_lat=request.end.lat,
            end_lng=request.end.lng,
            waypoints=waypoints_data,
            option=request.option,
        )
    except Exception as e:
        raise ExternalServiceError("경로를 찾을 수 없어요") from e

    # 경로 기록 저장 (PostGIS GEOGRAPHY 타입 사용)
    route_history = RouteHistory(
        id=uuid4(),
        profile_id=profile_id,
        start_name=request.start.name,
        start_point=make_point(request.start.lng, request.start.lat),
        end_name=request.end.name,
        end_point=make_point(request.end.lng, request.end.lat),
        waypoints=waypoints_data,
        route_option=request.option,
        total_distance_m=route_data["total_distance_m"],
        total_duration_s=route_data["total_duration_s"],
        path_data=route_data["path"],
        created_at=_utcnow(),
    )

    saved_route = _repository.create(session, route_history)

    return RouteSearchResponse(
        id=str(saved_route.id),
        start=PointResponse(
            name=saved_route.start_name,
            lat=saved_route.start_lat,
            lng=saved_route.start_lng,
        ),
        end=PointResponse(
            name=saved_route.end_name,
            lat=saved_route.end_lat,
            lng=saved_route.end_lng,
        ),
        total_distance_m=saved_route.total_distance_m,
        total_duration_s=saved_route.total_duration_s,
        distance_text=format_distance(saved_route.total_distance_m),
        duration_text=format_duration(saved_route.total_duration_s),
        path=saved_route.path_data,
    )


# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()


@router.post("/search", response_model=ApiResponse[RouteSearchResponse])
def search_route_endpoint(
    request: RouteSearchRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[RouteSearchResponse] | JSONResponse:
    """경로 검색"""
    from src.core.exceptions import RouteNotFoundError

    try:
        result = search_route(session, profile.id, request)

        return ApiResponse(
            status=Status.SUCCESS,
            message="경로 검색에 성공했어요",
            data=result,
        )
    except (RouteNotFoundError, ExternalServiceError):
        return JSONResponse(
            status_code=404,
            content={
                "status": Status.ROUTE_NOT_FOUND,
                "message": "경로를 찾을 수 없어요",
                "data": None,
            },
        )
