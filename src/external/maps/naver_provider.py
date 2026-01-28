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
"""

import httpx

from src.core.config import settings

# API 타임아웃 (초)
_TIMEOUT = 10.0


async def reverse_geocode(lng: float, lat: float) -> dict:
    """Naver Cloud Reverse Geocoding API 호출

    Args:
        lng: 경도 (longitude)
        lat: 위도 (latitude)

    Returns:
        Naver API 응답 (JSON)
    """
    url = "https://maps.apigw.ntruss.com/map-reversegeocode/v2/gc"
    headers = {
        "x-ncp-apigw-api-key-id": settings.NAVER_CLIENT_ID or "",
        "x-ncp-apigw-api-key": settings.NAVER_CLIENT_SECRET or "",
    }
    params = {
        "coords": f"{lng},{lat}",  # 경도,위도 순서
        "orders": "roadaddr,addr",
        "output": "json",
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


async def get_directions(
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
        httpx.HTTPStatusError: API 호출 실패
        KeyError: 응답 파싱 실패
    """
    url = "https://maps.apigw.ntruss.com/map-direction/v1/driving"
    headers = {
        "x-ncp-apigw-api-key-id": settings.NAVER_CLIENT_ID or "",
        "x-ncp-apigw-api-key": settings.NAVER_CLIENT_SECRET or "",
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

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

    # 응답 파싱: route.{option}[0]에서 데이터 추출
    route = data["route"][option][0]
    summary = route["summary"]

    return {
        "total_distance_m": summary["distance"],
        "total_duration_s": summary["duration"] // 1000,  # ms → s
        "path": route["path"],  # [[lng, lat], ...]
    }


async def search_places(query: str, display: int = 5) -> dict:
    """Naver Developers Local Search API 호출

    Args:
        query: 검색어
        display: 결과 개수 (최대 5개)

    Returns:
        Naver API 응답 (JSON)
    """
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": settings.NAVER_SEARCH_CLIENT_ID or "",
        "X-Naver-Client-Secret": settings.NAVER_SEARCH_CLIENT_SECRET or "",
    }
    params = {
        "query": query,
        "display": min(display, 5),  # API 최대 5개 제한
        "sort": "random",
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
