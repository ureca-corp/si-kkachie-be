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


@router.post("/search", response_model=ApiResponse[RouteSearchResponse])
def search_route(
    request: RouteSearchRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[RouteSearchResponse] | JSONResponse:
    """경로 검색"""
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
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": Status.ERROR_ROUTE_NOT_FOUND,
                "message": "경로를 찾을 수 없어요",
                "data": None,
            },
        )


@router.get("/recent", response_model=ApiResponse[list[RouteHistoryResponse]])
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
