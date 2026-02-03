"""카테고리별 장소 검색

GET /locations/search/category
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from src.core.deps import CurrentProfile
from src.core.exceptions import ExternalServiceError
from src.core.response import ApiResponse, Status
from src.external.kakao import get_kakao_provider

# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────


class PlaceCategoryItem(BaseModel):
    """카테고리 검색 결과 아이템"""

    id: str
    name: str
    category: str
    address: str
    road_address: str
    phone: str
    lat: float
    lng: float
    distance_m: int
    place_url: str


class PlaceCategoryResponse(BaseModel):
    """카테고리 검색 응답"""

    total_count: int
    page: int
    is_end: bool
    places: list[PlaceCategoryItem] = Field(default_factory=list)


# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────


async def search_places_by_category(
    category: str,
    lat: float,
    lng: float,
    radius: int = 1000,
    page: int = 1,
    size: int = 15,
) -> PlaceCategoryResponse:
    """카테고리별 장소 검색"""
    try:
        data = await get_kakao_provider().search_by_category(
            category=category,
            lng=lng,
            lat=lat,
            radius=radius,
            page=page,
            size=size,
            sort="distance",
        )
    except Exception as e:
        raise ExternalServiceError("장소 검색에 실패했어요") from e

    places = [PlaceCategoryItem(**place) for place in data["places"]]

    return PlaceCategoryResponse(
        total_count=data["total_count"],
        page=page,
        is_end=data["is_end"],
        places=places,
    )


# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()


@router.get("/search/category", response_model=ApiResponse[PlaceCategoryResponse])
async def search_category_endpoint(
    _profile: CurrentProfile,
    category: str = Query(..., description="카테고리 코드 (MT1, FD6, CE7 등)"),
    lat: float = Query(..., ge=-90, le=90, description="위도"),
    lng: float = Query(..., ge=-180, le=180, description="경도"),
    radius: int = Query(1000, ge=1, le=20000, description="검색 반경 (미터)"),
    page: int = Query(1, ge=1, le=45, description="페이지"),
    size: int = Query(15, ge=1, le=15, description="결과 개수"),
) -> ApiResponse[PlaceCategoryResponse]:
    """카테고리별 주변 장소 검색"""
    result = await search_places_by_category(
        category=category,
        lat=lat,
        lng=lng,
        radius=radius,
        page=page,
        size=size,
    )

    return ApiResponse(
        status=Status.SUCCESS,
        message="주변 장소를 찾았어요",
        data=result,
    )
