"""routes 도메인 Controller

SPEC 기반 API:
- POST /routes/search (경로 검색)
- GET /routes/recent (최근 경로 조회)
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from . import service
from .entities import (
    PointResponse,
    RouteHistoryResponse,
    RouteSearchRequest,
    RouteSearchResponse,
)

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post(
    "/search",
    response_model=ApiResponse[RouteSearchResponse],
    openapi_extra={
        "x-pages": ["route-search", "mission-play"],
        "x-agent-description": "경로 검색. 길찾기 페이지에서 출발지/도착지로 대중교통 경로를 검색할 때 사용. 외부 지도 API(TMAP 등) 연동",
    },
)
def search_route(
    request: RouteSearchRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[RouteSearchResponse] | JSONResponse:
    """경로 검색"""
    from src.core.exceptions import ExternalServiceError, RouteNotFoundError

    try:
        result = service.search_route(session, profile.id, request)

        return ApiResponse(
            status=Status.SUCCESS,
            message="경로 검색에 성공했어요",
            data=RouteSearchResponse(
                id=result["id"],
                start=PointResponse(**result["start"]),
                end=PointResponse(**result["end"]),
                total_distance_m=result["total_distance_m"],
                total_duration_s=result["total_duration_s"],
                distance_text=result["distance_text"],
                duration_text=result["duration_text"],
                path=result["path"],
            ),
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


@router.get(
    "/recent",
    response_model=ApiResponse[list[RouteHistoryResponse]],
    openapi_extra={
        "x-pages": ["route-search", "home"],
        "x-agent-description": "최근 검색 경로 목록 조회. 길찾기 페이지에서 최근 검색 기록을 보여주거나, 홈 화면에서 빠른 접근용으로 사용",
    },
)
def get_recent_routes(
    profile: CurrentProfile,
    session: Session = Depends(get_session),
    limit: int = Query(default=10, ge=1, le=50),
) -> ApiResponse[list[RouteHistoryResponse]]:
    """최근 경로 조회"""
    routes = service.get_recent_routes(session, profile.id, limit)

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
