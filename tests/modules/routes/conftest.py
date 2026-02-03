"""routes 도메인 테스트 픽스처"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlmodel import Session

from src.core.enums import RouteOption
from src.modules.profiles import Profile
from src.modules.routes._models import RouteHistory


def _utcnow() -> datetime:
    return datetime.now(UTC)


@pytest.fixture
def route_search_request() -> dict:
    """경로 검색 요청 데이터"""
    return {
        "start": {
            "name": "서울역",
            "lat": 37.5547,
            "lng": 126.9706,
        },
        "end": {
            "name": "강남역",
            "lat": 37.4979,
            "lng": 127.0276,
        },
        "option": "traoptimal",
    }


@pytest.fixture
def route_search_with_waypoints_request() -> dict:
    """경유지 포함 경로 검색 요청"""
    return {
        "start": {
            "name": "서울역",
            "lat": 37.5547,
            "lng": 126.9706,
        },
        "end": {
            "name": "강남역",
            "lat": 37.4979,
            "lng": 127.0276,
        },
        "waypoints": [
            {
                "name": "명동",
                "lat": 37.5636,
                "lng": 126.9869,
            },
        ],
        "option": "traoptimal",
    }


@pytest.fixture
def route_search_too_many_waypoints_request() -> dict:
    """경유지 초과 (6개) 경로 검색 요청"""
    return {
        "start": {
            "name": "서울역",
            "lat": 37.5547,
            "lng": 126.9706,
        },
        "end": {
            "name": "강남역",
            "lat": 37.4979,
            "lng": 127.0276,
        },
        "waypoints": [
            {"name": f"경유지{i}", "lat": 37.5 + i * 0.01, "lng": 127.0 + i * 0.01}
            for i in range(6)  # 6개 경유지 (최대 5개)
        ],
        "option": "traoptimal",
    }


@pytest.fixture
def created_route_history(session: Session, test_profile: Profile) -> RouteHistory:
    """DB에 저장된 경로 히스토리 (PostGIS GEOGRAPHY 사용)"""
    from src.modules.routes._models import make_point

    route = RouteHistory(
        id=uuid4(),
        profile_id=test_profile.id,
        start_name="서울역",
        start_point=make_point(126.9706, 37.5547),  # lng, lat 순서
        end_name="강남역",
        end_point=make_point(127.0276, 37.4979),  # lng, lat 순서
        waypoints=None,
        route_option=RouteOption.TRAOPTIMAL,
        total_distance_m=12500,
        total_duration_s=1800,
        path_data=[
            [126.9706, 37.5547],
            [126.9800, 37.5500],
            [127.0276, 37.4979],
        ],
        created_at=_utcnow(),
    )
    session.add(route)
    session.commit()
    session.refresh(route)
    return route
