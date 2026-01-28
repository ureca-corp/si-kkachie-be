"""locations 도메인

GPS 좌표 → 주소 변환 (Reverse Geocoding) 및 장소 검색 API

Vertical Slice 구조:
- reverse_geocode.py: GET /locations/reverse-geocode
- search.py: GET /locations/search
- _parsers.py: 공유 파싱 로직
- _utils.py: 공유 유틸리티
"""

from fastapi import APIRouter

from .reverse_geocode import router as reverse_geocode_router
from .search import router as search_router

router = APIRouter(prefix="/locations", tags=["locations"])
router.include_router(reverse_geocode_router)
router.include_router(search_router)
