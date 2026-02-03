"""경로 상세 조회 테스트

GET /routes/{route_id}

SPEC 기반 테스트 케이스:
- TC-R-005: 경로 상세 조회
- TC-R-104: 존재하지 않는 경로 상세 조회
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.modules.profiles import Profile
from src.modules.routes._models import RouteHistory


class TestRouteDetail:
    """GET /routes/{route_id} 테스트"""

    def test_get_route_detail_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_route_history: RouteHistory,
    ) -> None:
        """TC-R-005: 경로 상세 조회 성공"""
        route_id = str(created_route_history.id)
        response = auth_client.get(f"/routes/{route_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "경로 조회에 성공했어요"

        route = data["data"]
        assert route["id"] == route_id
        assert route["start"]["name"] == "서울역"
        assert route["start"]["lat"] == pytest.approx(37.5547, abs=0.001)
        assert route["start"]["lng"] == pytest.approx(126.9706, abs=0.001)
        assert route["end"]["name"] == "강남역"
        assert route["end"]["lat"] == pytest.approx(37.4979, abs=0.001)
        assert route["end"]["lng"] == pytest.approx(127.0276, abs=0.001)
        assert route["total_distance_m"] == 12500
        assert route["total_duration_s"] == 1800
        assert "distance_text" in route
        assert "duration_text" in route
        assert "path" in route
        assert len(route["path"]) >= 2

    def test_get_route_detail_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-R-104: 존재하지 않는 경로 -> 404"""
        fake_id = str(uuid4())
        response = auth_client.get(f"/routes/{fake_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "RESOURCE_NOT_FOUND"
