"""routes 도메인 Service"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Session

from src.core.exceptions import ExternalServiceError

from . import repository
from .entities import RouteSearchRequest
from .models import RouteHistory


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _format_distance(meters: int) -> str:
    """거리를 읽기 쉬운 형식으로 변환"""
    if meters < 1000:
        return f"{meters}m"
    km = meters / 1000
    return f"{km:.1f}km"


def _format_duration(seconds: int) -> str:
    """시간을 읽기 쉬운 형식으로 변환"""
    minutes = seconds // 60
    if minutes < 60:
        return f"약 {minutes}분"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"약 {hours}시간"
    return f"약 {hours}시간 {remaining_minutes}분"


def search_route_from_naver(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    waypoints: list[dict] | None = None,
    option: str = "traoptimal",
) -> dict:
    """Naver Maps Directions API 호출

    TODO: 실제 구현
    """
    # 임시 구현 (테스트용)
    return {
        "total_distance_m": 12500,
        "total_duration_s": 1800,
        "path": [
            {"lat": start_lat, "lng": start_lng},
            {"lat": end_lat, "lng": end_lng},
        ],
    }


def search_route(
    session: Session,
    profile_id: UUID,
    request: RouteSearchRequest,
) -> dict:
    """경로 검색 및 저장"""
    waypoints_data = None
    if request.waypoints:
        waypoints_data = [
            {"name": wp.name, "lat": wp.lat, "lng": wp.lng} for wp in request.waypoints
        ]

    try:
        # Naver API 호출
        route_data = search_route_from_naver(
            start_lat=request.start.lat,
            start_lng=request.start.lng,
            end_lat=request.end.lat,
            end_lng=request.end.lng,
            waypoints=waypoints_data,
            option=request.option,
        )
    except Exception as e:
        raise ExternalServiceError("경로를 찾을 수 없어요") from e

    # 경로 기록 저장
    route_history = RouteHistory(
        id=uuid4(),
        profile_id=profile_id,
        start_name=request.start.name,
        start_lat=request.start.lat,
        start_lng=request.start.lng,
        end_name=request.end.name,
        end_lat=request.end.lat,
        end_lng=request.end.lng,
        waypoints=waypoints_data,
        route_option=request.option,
        total_distance_m=route_data["total_distance_m"],
        total_duration_s=route_data["total_duration_s"],
        path_data=route_data["path"],
        created_at=_utcnow(),
    )

    saved_route = repository.create(session, route_history)

    return {
        "id": str(saved_route.id),
        "start": {
            "name": saved_route.start_name,
            "lat": saved_route.start_lat,
            "lng": saved_route.start_lng,
        },
        "end": {
            "name": saved_route.end_name,
            "lat": saved_route.end_lat,
            "lng": saved_route.end_lng,
        },
        "total_distance_m": saved_route.total_distance_m,
        "total_duration_s": saved_route.total_duration_s,
        "distance_text": _format_distance(saved_route.total_distance_m),
        "duration_text": _format_duration(saved_route.total_duration_s),
        "path": saved_route.path_data,
    }


def get_recent_routes(
    session: Session,
    profile_id: UUID,
    limit: int = 10,
) -> list[RouteHistory]:
    """최근 경로 조회"""
    # 최대 50개 제한
    limit = min(limit, 50)
    return repository.get_by_profile_id(session, profile_id, limit)
