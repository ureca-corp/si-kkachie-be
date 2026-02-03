"""장소 검색

GET /locations/search
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.exceptions import ExternalServiceError
from src.core.response import ApiResponse, Status
from src.external.naver import get_naver_provider

from ._parsers import parse_place_item
from ._utils import calculate_distance

# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────


class PlaceSearchItem(BaseModel):
    """장소 검색 결과 아이템"""

    id: str  # 장소 고유 ID
    name: str  # 장소명
    category: str  # 카테고리
    address: str  # 지번 주소
    road_address: str  # 도로명 주소
    lat: float
    lng: float
    distance: int | None = None  # 미터 단위 (현재 위치 제공 시)


# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────


async def search_places(
    session: Session,
    query: str,
    user_lat: float | None = None,
    user_lng: float | None = None,
    limit: int = 20,
) -> list[PlaceSearchItem]:
    """장소 검색

    Args:
        session: DB 세션 (거리 계산용)
        query: 검색어
        user_lat: 현재 위도 (선택, 거리 계산용)
        user_lng: 현재 경도 (선택, 거리 계산용)
        limit: 결과 개수 (최대 5개 제한)

    Returns:
        PlaceSearchItem 목록

    Raises:
        ExternalServiceError: API 호출 실패
    """
    try:
        data = await get_naver_provider().search_places(query, display=min(limit, 5))
    except Exception as e:
        raise ExternalServiceError("장소 검색에 실패했어요") from e

    items = [
        PlaceSearchItem(**parse_place_item(item))
        for item in data.get("items", [])
    ]

    # 현재 위치 제공 시 거리 계산
    if user_lat is not None and user_lng is not None:
        for item in items:
            item.distance = calculate_distance(
                session, user_lat, user_lng, item.lat, item.lng
            )

    return items


# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()


@router.get("/search", response_model=ApiResponse[list[PlaceSearchItem]])
async def search_places_endpoint(
    profile: CurrentProfile,
    query: str = Query(..., min_length=1, max_length=100, description="검색어"),
    lat: float | None = Query(None, ge=-90, le=90, description="현재 위도"),
    lng: float | None = Query(None, ge=-180, le=180, description="현재 경도"),
    limit: int = Query(20, ge=1, le=50, description="결과 개수"),
    session: Session = Depends(get_session),
) -> ApiResponse[list[PlaceSearchItem]]:
    """장소 검색"""
    results = await search_places(session, query, lat, lng, limit)

    return ApiResponse(
        status=Status.SUCCESS,
        message="검색에 성공했어요",
        data=results,
    )
