"""Naver API Provider

Naver Cloud Platform과 Naver Developers API 연동

API 목록:
1. Reverse Geocoding (Naver Cloud Platform) - 좌표 -> 주소 변환
2. Directions (Naver Cloud Platform) - 경로 검색
3. Local Search (Naver Developers) - 장소 검색
"""

from src.core.config import settings

from ._base import INaverProvider, NaverError
from ._client import close_client
from .directions import directions as _directions
from .local_search import search_places as _search_places
from .reverse_geocode import reverse_geocode as _reverse_geocode


class NaverProvider(INaverProvider):
    """Naver API Provider 구현"""

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        search_client_id: str | None = None,
        search_client_secret: str | None = None,
    ) -> None:
        """Naver Provider 초기화

        Args:
            client_id: Naver Cloud Platform API Key ID (None이면 settings에서 가져옴)
            client_secret: Naver Cloud Platform API Key (None이면 settings에서 가져옴)
            search_client_id: Naver Developers Client ID (None이면 settings에서 가져옴)
            search_client_secret: Naver Developers Client Secret (None이면 settings에서 가져옴)
        """
        self._client_id = client_id or settings.NAVER_CLIENT_ID or ""
        self._client_secret = client_secret or settings.NAVER_CLIENT_SECRET or ""
        self._search_client_id = search_client_id or settings.NAVER_SEARCH_CLIENT_ID or ""
        self._search_client_secret = (
            search_client_secret or settings.NAVER_SEARCH_CLIENT_SECRET or ""
        )

    async def reverse_geocode(self, lng: float, lat: float) -> dict:
        """좌표 -> 주소 변환"""
        return await _reverse_geocode(lng, lat, self._client_id, self._client_secret)

    async def search_places(self, query: str, display: int = 5) -> dict:
        """장소 검색"""
        return await _search_places(
            query, self._search_client_id, self._search_client_secret, display
        )

    async def directions(
        self,
        start_lng: float,
        start_lat: float,
        goal_lng: float,
        goal_lat: float,
        waypoints: list[tuple[float, float]] | None = None,
        option: str = "traoptimal",
    ) -> dict:
        """경로 검색"""
        return await _directions(
            start_lng,
            start_lat,
            goal_lng,
            goal_lat,
            self._client_id,
            self._client_secret,
            waypoints,
            option,
        )

    async def close(self) -> None:
        """HTTP 클라이언트 종료"""
        await close_client()


# 싱글톤 인스턴스
_instance: NaverProvider | None = None


def get_naver_provider() -> NaverProvider:
    """Naver Provider 싱글톤 반환"""
    global _instance
    if _instance is None:
        _instance = NaverProvider()
    return _instance


__all__ = [
    # 인터페이스
    "INaverProvider",
    # Provider 클래스
    "NaverProvider",
    # 팩토리 함수
    "get_naver_provider",
    # 에러 클래스
    "NaverError",
]
