"""위치 관련 유틸리티

공유 모듈: PostGIS 거리 계산
"""

from geoalchemy2 import Geography
from sqlalchemy import cast, func, select
from sqlmodel import Session


def calculate_distance(
    session: Session,
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float,
) -> int:
    """PostGIS ST_Distance로 두 좌표 간 직선거리(m) 계산

    GeoAlchemy2 func 사용, GEOGRAPHY 타입으로 지구 곡률 반영

    Args:
        session: DB 세션
        from_lat: 시작점 위도
        from_lng: 시작점 경도
        to_lat: 도착점 위도
        to_lng: 도착점 경도

    Returns:
        거리 (미터 단위, 정수)
    """
    from_point = cast(
        func.ST_SetSRID(func.ST_MakePoint(from_lng, from_lat), 4326),
        Geography,
    )
    to_point = cast(
        func.ST_SetSRID(func.ST_MakePoint(to_lng, to_lat), 4326),
        Geography,
    )

    result = session.exec(select(func.ST_Distance(from_point, to_point)))  # type: ignore[call-overload]
    distance = result.one_or_none()
    return int(distance) if distance else 0
