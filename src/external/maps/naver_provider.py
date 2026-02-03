"""Naver Maps API Provider

Naver Cloud Platform과 Naver Developers API 호출을 담당합니다.

API 스펙:
1. Reverse Geocoding (Naver Cloud Platform)
   - Endpoint: https://maps.apigw.ntruss.com/map-reversegeocode/v2/gc
   - Headers: x-ncp-apigw-api-key-id, x-ncp-apigw-api-key
   - coords는 경도,위도 순서 (lng,lat)

2. Local Search (Naver Developers)
   - Endpoint: https://openapi.naver.com/v1/search/local.json
   - Headers: X-Naver-Client-Id, X-Naver-Client-Secret
   - display 최대 5개

3. Directions (Naver Cloud Platform)
   - Endpoint: https://maps.apigw.ntruss.com/map-direction/v1/driving
"""

import httpx

from src.core.config import settings

from .base import INaverMapsProvider, NaverMapsError

# API 타임아웃 (초)
_TIMEOUT = 10.0


class NaverMapsProvider(INaverMapsProvider):
    """Naver Maps API Provider 구현"""

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        search_client_id: str | None = None,
        search_client_secret: str | None = None,
    ) -> None:
        """Naver Maps Provider 초기화

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
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """공유 HTTP 클라이언트 반환 (lazy initialization)"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=_TIMEOUT)
        return self._client

    async def close(self) -> None:
        """HTTP 클라이언트 종료"""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def reverse_geocode(self, lng: float, lat: float) -> dict:
        """Naver Cloud Reverse Geocoding API 호출

        Args:
            lng: 경도 (longitude)
            lat: 위도 (latitude)

        Returns:
            Naver API 응답 (JSON)

        Raises:
            NaverMapsError: API 호출 실패
        """
        url = "https://maps.apigw.ntruss.com/map-reversegeocode/v2/gc"
        headers = {
            "x-ncp-apigw-api-key-id": self._client_id,
            "x-ncp-apigw-api-key": self._client_secret,
        }
        params = {
            "coords": f"{lng},{lat}",  # 경도,위도 순서
            "orders": "roadaddr,addr",
            "output": "json",
        }

        try:
            client = await self._get_client()
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise NaverMapsError(
                f"Reverse geocode API 호출 실패: {e.response.status_code}",
                code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise NaverMapsError(f"Reverse geocode API 요청 실패: {e}") from e

    async def get_directions(
        self,
        start_lng: float,
        start_lat: float,
        goal_lng: float,
        goal_lat: float,
        waypoints: list[tuple[float, float]] | None = None,
        option: str = "traoptimal",
    ) -> dict:
        """Naver Cloud Directions API 호출

        Args:
            start_lng: 출발지 경도
            start_lat: 출발지 위도
            goal_lng: 도착지 경도
            goal_lat: 도착지 위도
            waypoints: 경유지 리스트 [(lng, lat), ...]
            option: 경로 옵션 (traoptimal, trafast, tracomfort 등)

        Returns:
            dict: {
                "total_distance_m": int,
                "total_duration_s": int (밀리초를 초로 변환),
                "path": [[lng, lat], ...] 좌표 배열
            }

        Raises:
            NaverMapsError: API 호출 실패
        """
        url = "https://maps.apigw.ntruss.com/map-direction/v1/driving"
        headers = {
            "x-ncp-apigw-api-key-id": self._client_id,
            "x-ncp-apigw-api-key": self._client_secret,
        }
        params = {
            "start": f"{start_lng},{start_lat}",
            "goal": f"{goal_lng},{goal_lat}",
            "option": option,
        }

        # 경유지 추가 (최대 5개)
        if waypoints:
            waypoint_str = ":".join(f"{lng},{lat}" for lng, lat in waypoints[:5])
            params["waypoints"] = waypoint_str

        try:
            client = await self._get_client()
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            raise NaverMapsError(
                f"Directions API 호출 실패: {e.response.status_code}",
                code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise NaverMapsError(f"Directions API 요청 실패: {e}") from e

        # 응답 파싱: route.{option}[0]에서 데이터 추출
        try:
            route = data["route"][option][0]
            summary = route["summary"]
            return {
                "total_distance_m": summary["distance"],
                "total_duration_s": summary["duration"] // 1000,  # ms → s
                "path": route["path"],  # [[lng, lat], ...]
            }
        except (KeyError, IndexError, TypeError) as e:
            raise NaverMapsError(f"Directions API 응답 파싱 실패: {e}") from e

    async def search_places(self, query: str, display: int = 5) -> dict:
        """Naver Developers Local Search API 호출

        Args:
            query: 검색어
            display: 결과 개수 (최대 5개)

        Returns:
            Naver API 응답 (JSON)

        Raises:
            NaverMapsError: API 호출 실패
        """
        url = "https://openapi.naver.com/v1/search/local.json"
        headers = {
            "X-Naver-Client-Id": self._search_client_id,
            "X-Naver-Client-Secret": self._search_client_secret,
        }
        params = {
            "query": query,
            "display": min(display, 5),  # API 최대 5개 제한
            "sort": "random",
        }

        try:
            client = await self._get_client()
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise NaverMapsError(
                f"Search API 호출 실패: {e.response.status_code}",
                code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise NaverMapsError(f"Search API 요청 실패: {e}") from e


# ─────────────────────────────────────────────────
# 하위 호환성을 위한 모듈 수준 함수
# 기존: from src.external.maps import naver_provider
#       await naver_provider.search_places(...)
# ─────────────────────────────────────────────────

_instance: NaverMapsProvider | None = None


def _get_instance() -> NaverMapsProvider:
    """싱글톤 인스턴스 반환"""
    global _instance
    if _instance is None:
        _instance = NaverMapsProvider()
    return _instance


async def reverse_geocode(lng: float, lat: float) -> dict:
    """좌표 → 주소 변환 (하위 호환성)"""
    return await _get_instance().reverse_geocode(lng, lat)


async def get_directions(
    start_lng: float,
    start_lat: float,
    goal_lng: float,
    goal_lat: float,
    waypoints: list[tuple[float, float]] | None = None,
    option: str = "traoptimal",
) -> dict:
    """경로 검색 (하위 호환성)"""
    return await _get_instance().get_directions(
        start_lng, start_lat, goal_lng, goal_lat, waypoints, option
    )


async def search_places(query: str, display: int = 5) -> dict:
    """장소 검색 (하위 호환성)"""
    return await _get_instance().search_places(query, display)
