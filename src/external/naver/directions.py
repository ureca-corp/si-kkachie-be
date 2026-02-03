"""Naver Cloud Platform Directions API

경로 검색

Endpoint: https://maps.apigw.ntruss.com/map-direction/v1/driving
"""

import httpx

from ._base import NaverError
from ._client import get_client


async def directions(
    start_lng: float,
    start_lat: float,
    goal_lng: float,
    goal_lat: float,
    client_id: str,
    client_secret: str,
    waypoints: list[tuple[float, float]] | None = None,
    option: str = "traoptimal",
) -> dict:
    """Naver Cloud Directions API 호출

    Args:
        start_lng: 출발지 경도
        start_lat: 출발지 위도
        goal_lng: 도착지 경도
        goal_lat: 도착지 위도
        client_id: Naver Cloud Platform API Key ID
        client_secret: Naver Cloud Platform API Key
        waypoints: 경유지 리스트 [(lng, lat), ...]
        option: 경로 옵션 (traoptimal, trafast, tracomfort 등)

    Returns:
        dict: {
            "total_distance_m": int,
            "total_duration_s": int (밀리초를 초로 변환),
            "path": [[lng, lat], ...] 좌표 배열
        }

    Raises:
        NaverError: API 호출 실패
    """
    url = "https://maps.apigw.ntruss.com/map-direction/v1/driving"
    headers = {
        "x-ncp-apigw-api-key-id": client_id,
        "x-ncp-apigw-api-key": client_secret,
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
        client = await get_client()
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as e:
        raise NaverError(
            f"Directions API 호출 실패: {e.response.status_code}",
            code=e.response.status_code,
        ) from e
    except httpx.RequestError as e:
        raise NaverError(f"Directions API 요청 실패: {e}") from e

    # 응답 파싱: route.{option}[0]에서 데이터 추출
    try:
        route = data["route"][option][0]
        summary = route["summary"]
        return {
            "total_distance_m": summary["distance"],
            "total_duration_s": summary["duration"] // 1000,  # ms -> s
            "path": route["path"],  # [[lng, lat], ...]
        }
    except (KeyError, IndexError, TypeError) as e:
        raise NaverError(f"Directions API 응답 파싱 실패: {e}") from e
