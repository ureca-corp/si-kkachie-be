"""Kakao Local Category Search API

카테고리별 장소 검색

Endpoint: https://dapi.kakao.com/v2/local/search/category.json
공식 문서: https://developers.kakao.com/docs/latest/ko/local/dev-guide
"""

import httpx

from ._base import KakaoError
from ._client import get_client


async def search_by_category(
    category: str,
    lng: float,
    lat: float,
    api_key: str,
    radius: int = 1000,
    page: int = 1,
    size: int = 15,
    sort: str = "distance",
) -> dict:
    """카카오 로컬 API - 카테고리로 장소 검색

    Args:
        category: 카테고리 코드 (MT1, CS2, FD6, CE7 등)
        lng: 경도 (x)
        lat: 위도 (y)
        api_key: Kakao REST API Key
        radius: 검색 반경 미터 (기본 1000, 최대 20000)
        page: 페이지 번호 (기본 1, 최대 45)
        size: 결과 개수 (기본 15, 최대 15)
        sort: 정렬 기준 (distance 또는 accuracy)

    Returns:
        dict: {
            "total_count": int,
            "is_end": bool,
            "places": [
                {
                    "id": str,
                    "name": str,
                    "category": str,
                    "address": str,
                    "road_address": str,
                    "phone": str,
                    "lat": float,
                    "lng": float,
                    "distance_m": int,
                    "place_url": str,
                }
            ]
        }

    Raises:
        KakaoError: API 호출 실패
    """
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {
        "Authorization": f"KakaoAK {api_key}",
    }
    params = {
        "category_group_code": category,
        "x": str(lng),
        "y": str(lat),
        "radius": min(radius, 20000),
        "page": min(page, 45),
        "size": min(size, 15),
        "sort": sort,
    }

    try:
        client = await get_client()
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as e:
        raise KakaoError(
            f"Category Search API 호출 실패: {e.response.status_code}",
            code=e.response.status_code,
        ) from e
    except httpx.RequestError as e:
        raise KakaoError(f"Category Search API 요청 실패: {e}") from e

    meta = data.get("meta", {})
    documents = data.get("documents", [])

    places = [
        {
            "id": doc.get("id", ""),
            "name": doc.get("place_name", ""),
            "category": doc.get("category_name", ""),
            "address": doc.get("address_name", ""),
            "road_address": doc.get("road_address_name", ""),
            "phone": doc.get("phone", ""),
            "lat": float(doc.get("y", 0)),
            "lng": float(doc.get("x", 0)),
            "distance_m": int(doc.get("distance", 0)),
            "place_url": doc.get("place_url", ""),
        }
        for doc in documents
    ]

    return {
        "total_count": meta.get("total_count", 0),
        "is_end": meta.get("is_end", True),
        "places": places,
    }
