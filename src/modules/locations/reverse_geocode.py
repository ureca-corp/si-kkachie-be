"""GPS 좌표 → 주소 변환 (Reverse Geocoding)

GET /locations/reverse-geocode
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.core.deps import CurrentProfile
from src.core.exceptions import ExternalServiceError, LocationNotFoundError
from src.core.response import ApiResponse, Status
from src.external.naver import get_naver_provider

from ._parsers import parse_reverse_geocode_response

# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────


class ReverseGeocodeResponse(BaseModel):
    """GPS 좌표 → 주소 변환 응답"""

    name: str  # 건물명 또는 도로명 기반 표시
    address: str  # 지번 주소
    road_address: str  # 도로명 주소
    lat: float
    lng: float


# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────


async def get_reverse_geocode(lat: float, lng: float) -> ReverseGeocodeResponse:
    """좌표 → 주소 변환

    Args:
        lat: 위도
        lng: 경도

    Returns:
        ReverseGeocodeResponse

    Raises:
        ExternalServiceError: API 호출 실패
        LocationNotFoundError: 해당 좌표의 주소를 찾을 수 없음
    """
    try:
        data = await get_naver_provider().reverse_geocode(lng, lat)
    except Exception as e:
        raise ExternalServiceError("위치 정보를 가져올 수 없어요") from e

    # Naver API status code 확인
    status = data.get("status", {})
    if status.get("code") != 0 or not data.get("results"):
        raise LocationNotFoundError("해당 좌표의 주소를 찾을 수 없어요")

    name, address, road_address = parse_reverse_geocode_response(data, lat, lng)

    return ReverseGeocodeResponse(
        name=name,
        address=address,
        road_address=road_address,
        lat=lat,
        lng=lng,
    )


# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()


@router.get("/reverse-geocode", response_model=ApiResponse[ReverseGeocodeResponse])
async def reverse_geocode(
    profile: CurrentProfile,
    lat: float = Query(..., ge=-90, le=90, description="위도"),
    lng: float = Query(..., ge=-180, le=180, description="경도"),
) -> ApiResponse[ReverseGeocodeResponse]:
    """GPS 좌표를 주소로 변환"""
    result = await get_reverse_geocode(lat, lng)

    return ApiResponse(
        status=Status.SUCCESS,
        message="위치 정보를 가져왔어요",
        data=result,
    )
