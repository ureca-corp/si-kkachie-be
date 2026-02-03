"""Naver Cloud Platform Reverse Geocoding API

좌표 -> 주소 변환

Endpoint: https://maps.apigw.ntruss.com/map-reversegeocode/v2/gc
Headers: x-ncp-apigw-api-key-id, x-ncp-apigw-api-key
coords는 경도,위도 순서 (lng,lat)
"""

import httpx

from ._base import NaverError
from ._client import get_client


async def reverse_geocode(
    lng: float,
    lat: float,
    client_id: str,
    client_secret: str,
) -> dict:
    """Naver Cloud Reverse Geocoding API 호출

    Args:
        lng: 경도 (longitude)
        lat: 위도 (latitude)
        client_id: Naver Cloud Platform API Key ID
        client_secret: Naver Cloud Platform API Key

    Returns:
        Naver API 응답 (JSON)

    Raises:
        NaverError: API 호출 실패
    """
    url = "https://maps.apigw.ntruss.com/map-reversegeocode/v2/gc"
    headers = {
        "x-ncp-apigw-api-key-id": client_id,
        "x-ncp-apigw-api-key": client_secret,
    }
    params = {
        "coords": f"{lng},{lat}",  # 경도,위도 순서
        "orders": "roadaddr,addr",
        "output": "json",
    }

    try:
        client = await get_client()
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise NaverError(
            f"Reverse geocode API 호출 실패: {e.response.status_code}",
            code=e.response.status_code,
        ) from e
    except httpx.RequestError as e:
        raise NaverError(f"Reverse geocode API 요청 실패: {e}") from e
