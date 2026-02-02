"""Kakao Mobility API Provider

카카오 모빌리티 길찾기 API 호출을 담당합니다.

API 스펙:
- Endpoint: https://apis-navi.kakaomobility.com/v1/directions
- Header: Authorization: KakaoAK {REST_API_KEY}
- 공식 문서: https://developers.kakaomobility.com/docs/navi-api/directions/

Result Code:
- 0: 성공
- 1: 길찾기 결과 없음
- 101-103: 출발지/도착지/경유지 도로 탐색 불가
- 104: 출발지와 도착지가 5m 이내
- 105-107: 교통 장애 존재
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
