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
