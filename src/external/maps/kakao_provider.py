"""Kakao API Provider

카카오 모빌리티 및 로컬 API 호출을 담당합니다.

API 스펙:
1. Directions (모빌리티)
   - Endpoint: https://apis-navi.kakaomobility.com/v1/directions
   - 공식 문서: https://developers.kakaomobility.com/docs/navi-api/directions/

2. Category Search (로컬)
   - Endpoint: https://dapi.kakao.com/v2/local/search/category.json
   - 공식 문서: https://developers.kakao.com/docs/latest/ko/local/dev-guide

공통:
- Header: Authorization: KakaoAK {REST_API_KEY}
"""

import httpx

from src.core.config import settings


class KakaoDirectionsError(Exception):
    """카카오 길찾기 API 에러"""

    def __init__(self, result_code: int, result_msg: str):
        self.result_code = result_code
        self.result_msg = result_msg
        super().__init__(f"[{result_code}] {result_msg}")


# API 타임아웃 (초)
_TIMEOUT = 10.0

# 네이버 옵션 → 카카오 priority 매핑
_OPTION_MAPPING = {
    "traoptimal": "RECOMMEND",  # 추천 경로
    "trafast": "TIME",  # 최단 시간
    "tracomfort": "RECOMMEND",  # 편한 길 (카카오에 동일 옵션 없음)
    "traavoidtoll": "RECOMMEND",  # 무료 우선 (별도 avoid 파라미터 필요)
    "traavoidcaronly": "RECOMMEND",  # 자동차 전용 회피
}


async def get_directions(
    start_lng: float,
    start_lat: float,
    goal_lng: float,
    goal_lat: float,
    waypoints: list[tuple[float, float]] | None = None,
    option: str = "traoptimal",
) -> dict:
    """Kakao Mobility Directions API 호출

    Args:
        start_lng: 출발지 경도
        start_lat: 출발지 위도
        goal_lng: 도착지 경도
        goal_lat: 도착지 위도
        waypoints: 경유지 리스트 [(lng, lat), ...]
        option: 경로 옵션 (traoptimal, trafast 등 - 네이버 호환)

    Returns:
        dict: {
            "total_distance_m": int,
            "total_duration_s": int,
            "path": [[lng, lat], ...] 좌표 배열
        }

    Raises:
        httpx.HTTPStatusError: HTTP 요청 실패
        KakaoDirectionsError: 경로 탐색 실패 (result_code != 0)
    """
    url = "https://apis-navi.kakaomobility.com/v1/directions"
    headers = {
        "Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY or ''}",
        "Content-Type": "application/json",
    }

    # 카카오 API는 X,Y (경도,위도) 형식
    params = {
        "origin": f"{start_lng},{start_lat}",
        "destination": f"{goal_lng},{goal_lat}",
        "priority": _OPTION_MAPPING.get(option, "RECOMMEND"),
        "summary": "false",  # 상세 정보 포함 (path 추출 위해)
    }

    # 경유지 추가 (최대 5개, "|"로 구분)
    if waypoints:
        waypoint_str = "|".join(f"{lng},{lat}" for lng, lat in waypoints[:5])
        params["waypoints"] = waypoint_str

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

    # result_code 확인 (0 = 성공)
    result_code = data.get("result_code", -1)
    if result_code != 0:
        result_msg = data.get("result_msg", "알 수 없는 오류")
        raise KakaoDirectionsError(result_code, result_msg)

    # routes 배열 확인
    routes = data.get("routes", [])
    if not routes:
        raise KakaoDirectionsError(-1, "경로 정보가 없습니다")

    route = routes[0]
    summary = route.get("summary", {})

    # path 추출: sections의 roads에서 vertexes 수집
    sections = route.get("sections", [])
    path = _extract_path(sections) if sections else []

    return {
        "total_distance_m": summary.get("distance", 0),
        "total_duration_s": summary.get("duration", 0),
        "path": path,
    }


def _extract_path(sections: list[dict]) -> list[list[float]]:
    """sections에서 경로 좌표 추출

    카카오 API의 vertexes는 [x1, y1, x2, y2, ...] 형태의 1차원 배열
    이를 [[lng, lat], [lng, lat], ...] 형태로 변환
    """
    path: list[list[float]] = []
    for section in sections:
        for road in section.get("roads", []):
            vertexes = road.get("vertexes", [])
            # vertexes는 [x1, y1, x2, y2, ...] 형태를 [[x, y], ...] 로 변환
            path.extend(
                [vertexes[i], vertexes[i + 1]] for i in range(0, len(vertexes) - 1, 2)
            )
    return path


# ─────────────────────────────────────────────────
# Category Search (로컬 API)
# ─────────────────────────────────────────────────


async def search_by_category(
    category: str,
    lng: float,
    lat: float,
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
        httpx.HTTPStatusError: HTTP 요청 실패
    """
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {
        "Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY or ''}",
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

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

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
