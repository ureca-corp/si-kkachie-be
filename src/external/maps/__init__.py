"""Maps external module

지도/경로 API 연동을 위한 외부 모듈
- 경로 검색: Kakao Mobility API
- 역지오코딩/장소검색: Naver Maps API
"""

from .base import (
    IDirectionsProvider,
    IKakaoMapsProvider,
    INaverMapsProvider,
    KakaoMapsError,
    MapsError,
    NaverMapsError,
)
from .kakao_provider import KakaoDirectionsError, KakaoMapsProvider
from .naver_provider import NaverMapsProvider

# ─────────────────────────────────────────────────
# 싱글톤 인스턴스 관리
# ─────────────────────────────────────────────────

_naver_instance: NaverMapsProvider | None = None
_kakao_instance: KakaoMapsProvider | None = None


def get_naver_provider() -> NaverMapsProvider:
    """Naver Maps Provider 싱글톤 반환"""
    global _naver_instance
    if _naver_instance is None:
        _naver_instance = NaverMapsProvider()
    return _naver_instance


def get_kakao_provider() -> KakaoMapsProvider:
    """Kakao Maps Provider 싱글톤 반환"""
    global _kakao_instance
    if _kakao_instance is None:
        _kakao_instance = KakaoMapsProvider()
    return _kakao_instance


# ─────────────────────────────────────────────────
# 하위 호환성을 위한 모듈 수준 프록시
# 기존: from src.external.maps import naver_provider
#       await naver_provider.search_places(...)
# ─────────────────────────────────────────────────


class _NaverProviderProxy:
    """naver_provider 모듈 호환을 위한 프록시 클래스"""

    async def reverse_geocode(self, lng: float, lat: float) -> dict:
        return await get_naver_provider().reverse_geocode(lng, lat)

    async def get_directions(
        self,
        start_lng: float,
        start_lat: float,
        goal_lng: float,
        goal_lat: float,
        waypoints: list[tuple[float, float]] | None = None,
        option: str = "traoptimal",
    ) -> dict:
        return await get_naver_provider().get_directions(
            start_lng, start_lat, goal_lng, goal_lat, waypoints, option
        )

    async def search_places(self, query: str, display: int = 5) -> dict:
        return await get_naver_provider().search_places(query, display)


class _KakaoProviderProxy:
    """kakao_provider 모듈 호환을 위한 프록시 클래스"""

    async def get_directions(
        self,
        start_lng: float,
        start_lat: float,
        goal_lng: float,
        goal_lat: float,
        waypoints: list[tuple[float, float]] | None = None,
        option: str = "traoptimal",
    ) -> dict:
        return await get_kakao_provider().get_directions(
            start_lng, start_lat, goal_lng, goal_lat, waypoints, option
        )

    async def search_by_category(
        self,
        category: str,
        lng: float,
        lat: float,
        radius: int = 1000,
        page: int = 1,
        size: int = 15,
        sort: str = "distance",
    ) -> dict:
        return await get_kakao_provider().search_by_category(
            category, lng, lat, radius, page, size, sort
        )


# 프록시 인스턴스 (기존 import 호환)
naver_provider = _NaverProviderProxy()
kakao_provider = _KakaoProviderProxy()


__all__ = [
    # 인터페이스
    "IDirectionsProvider",
    "INaverMapsProvider",
    "IKakaoMapsProvider",
    # Provider 클래스
    "NaverMapsProvider",
    "KakaoMapsProvider",
    # 팩토리 함수
    "get_naver_provider",
    "get_kakao_provider",
    # 에러 클래스
    "MapsError",
    "NaverMapsError",
    "KakaoMapsError",
    "KakaoDirectionsError",  # 하위 호환성
    # 프록시 (하위 호환성)
    "naver_provider",
    "kakao_provider",
]
