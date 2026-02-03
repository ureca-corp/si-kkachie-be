"""Naver Developers Local Search API

장소 검색

Endpoint: https://openapi.naver.com/v1/search/local.json
Headers: X-Naver-Client-Id, X-Naver-Client-Secret
display 최대 5개
"""

import httpx

from ._base import NaverError
from ._client import get_client


async def search_places(
    query: str,
    search_client_id: str,
    search_client_secret: str,
    display: int = 5,
) -> dict:
    """Naver Developers Local Search API 호출

    Args:
        query: 검색어
        search_client_id: Naver Developers Client ID
        search_client_secret: Naver Developers Client Secret
        display: 결과 개수 (최대 5개)

    Returns:
        Naver API 응답 (JSON)

    Raises:
        NaverError: API 호출 실패
    """
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": search_client_id,
        "X-Naver-Client-Secret": search_client_secret,
    }
    params = {
        "query": query,
        "display": min(display, 5),  # API 최대 5개 제한
        "sort": "random",
    }

    try:
        client = await get_client()
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise NaverError(
            f"Search API 호출 실패: {e.response.status_code}",
            code=e.response.status_code,
        ) from e
    except httpx.RequestError as e:
        raise NaverError(f"Search API 요청 실패: {e}") from e
