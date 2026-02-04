"""Kakao Mobility Directions API

경로 검색

Endpoint: https://apis-navi.kakaomobility.com/v1/directions
공식 문서: https://developers.kakaomobility.com/docs/navi-api/directions/
"""

import httpx

from ._base import KakaoError
from ._client import get_client

# 네이버 옵션 -> 카카오 priority 매핑
_OPTION_MAPPING = {
    "traoptimal": "RECOMMEND",  # 추천 경로
    "trafast": "TIME",  # 최단 시간
    "tracomfort": "RECOMMEND",  # 편한 길 (카카오에 동일 옵션 없음)
    "traavoidtoll": "RECOMMEND",  # 무료 우선 (별도 avoid 파라미터 필요)
    "traavoidcaronly": "RECOMMEND",  # 자동차 전용 회피
}


async def directions(
    start_lng: float,
    start_lat: float,
    goal_lng: float,
    goal_lat: float,
    api_key: str,
    waypoints: list[tuple[float, float]] | None = None,
    option: str = "traoptimal",
) -> dict:
    """Kakao Mobility Directions API 호출

    Args:
        start_lng: 출발지 경도
        start_lat: 출발지 위도
        goal_lng: 도착지 경도
        goal_lat: 도착지 위도
        api_key: Kakao REST API Key
        waypoints: 경유지 리스트 [(lng, lat), ...]
        option: 경로 옵션 (traoptimal, trafast 등 - 네이버 호환)

    Returns:
        dict: {
            "total_distance_m": int,
            "total_duration_s": int,
            "path": [[lng, lat], ...] 좌표 배열
        }

    Raises:
        KakaoError: API 호출 실패 또는 경로 탐색 실패
    """
    url = "https://apis-navi.kakaomobility.com/v1/directions"
    headers = {
        "Authorization": f"KakaoAK {api_key}",
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

    try:
        client = await get_client()
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as e:
        raise KakaoError(
            f"Directions API 호출 실패: {e.response.status_code}",
            code=e.response.status_code,
        ) from e
    except httpx.RequestError as e:
        raise KakaoError(f"Directions API 요청 실패: {e}") from e

    # routes 배열 확인
    routes = data.get("routes", [])
    if not routes:
        raise KakaoError("경로 정보가 없습니다", code=-1)

    route = routes[0]

    # result_code 확인 (0 = 성공) - routes[0] 내부에 있음
    result_code = route.get("result_code", -1)
    if result_code != 0:
        result_msg = route.get("result_msg", "알 수 없는 오류")
        raise KakaoError(f"[{result_code}] {result_msg}", code=result_code)

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
