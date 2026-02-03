"""Kakao API Provider

카카오 모빌리티 및 로컬 API 연동

API 목록:
1. Directions (모빌리티) - 경로 검색
2. Category Search (로컬) - 카테고리별 장소 검색
"""

from src.core.config import settings

from ._base import IKakaoProvider, KakaoError
from ._client import close_client
from .category_search import search_by_category as _search_by_category
from .directions import directions as _directions


class KakaoProvider(IKakaoProvider):
    """Kakao API Provider 구현"""

    def __init__(self, api_key: str | None = None) -> None:
        """Kakao Provider 초기화

        Args:
            api_key: Kakao REST API Key (None이면 settings에서 가져옴)
        """
        self._api_key = api_key or settings.KAKAO_REST_API_KEY or ""

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
            self._api_key,
            waypoints,
            option,
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
        """카테고리별 장소 검색"""
        return await _search_by_category(
            category,
            lng,
            lat,
            self._api_key,
            radius,
            page,
            size,
            sort,
        )

    async def close(self) -> None:
        """HTTP 클라이언트 종료"""
        await close_client()


# 싱글톤 인스턴스
_instance: KakaoProvider | None = None


def get_kakao_provider() -> KakaoProvider:
    """Kakao Provider 싱글톤 반환"""
    global _instance
    if _instance is None:
        _instance = KakaoProvider()
    return _instance


__all__ = [
    "IKakaoProvider",
    "KakaoError",
    "KakaoProvider",
    "get_kakao_provider",
]
