"""최근 경로 조회 테스트

GET /routes/recent

SPEC 기반 테스트 케이스:
- TC-R-004: 최근 경로 조회
"""

from fastapi.testclient import TestClient

from src.modules.profiles import Profile
from src.modules.routes._models import RouteHistory


class TestRecentRoutes:
    """GET /routes/recent 테스트"""

    def test_get_recent_routes_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_route_history: RouteHistory,
    ) -> None:
        """TC-R-004: 최근 경로 조회 성공"""
        response = auth_client.get("/routes/recent")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "조회에 성공했어요"
        assert len(data["data"]) >= 1

        route = data["data"][0]
        assert "id" in route
        assert "start_name" in route
        assert "end_name" in route
        assert "total_distance_m" in route
        assert "total_duration_s" in route
        assert "created_at" in route

    def test_get_recent_routes_with_limit(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_route_history: RouteHistory,
    ) -> None:
        """limit 파라미터 테스트"""
        response = auth_client.get("/routes/recent?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 5

    def test_get_recent_routes_empty(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """경로 기록이 없을 때 빈 목록"""
        response = auth_client.get("/routes/recent")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []

    def test_get_recent_routes_max_limit(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """limit 최대값 (50) 초과 시"""
        response = auth_client.get("/routes/recent?limit=100")

        # 최대 50개로 제한되거나 에러
        assert response.status_code in [200, 422]
