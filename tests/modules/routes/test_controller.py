"""routes 도메인 컨트롤러 테스트

SPEC 기반 테스트 케이스:
- TC-R-001: 기본 경로 검색
- TC-R-002: 경유지 포함 검색
- TC-R-003: 옵션 변경 검색
- TC-R-004: 최근 경로 조회
- TC-R-101: 경로 없음
- TC-R-102: 잘못된 좌표
- TC-R-103: 경유지 초과
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.modules.profiles.models import Profile
from src.modules.routes.models import RouteHistory


class TestSearchRoute:
    """POST /routes/search 테스트"""

    def test_search_route_basic_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        route_search_request: dict,
    ) -> None:
        """TC-R-001: 기본 경로 검색 성공"""
        with patch(
            "src.modules.routes.service.search_route_from_naver"
        ) as mock_naver:
            mock_naver.return_value = {
                "total_distance_m": 12500,
                "total_duration_s": 1800,
                "path": [
                    {"lat": 37.5547, "lng": 126.9706},
                    {"lat": 37.5500, "lng": 126.9800},
                    {"lat": 37.4979, "lng": 127.0276},
                ],
            }

            response = auth_client.post("/routes/search", json=route_search_request)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "경로 검색에 성공했어요"
        assert "id" in data["data"]
        assert data["data"]["start"]["name"] == "서울역"
        assert data["data"]["end"]["name"] == "강남역"
        assert data["data"]["total_distance_m"] == 12500
        assert data["data"]["total_duration_s"] == 1800
        assert "distance_text" in data["data"]  # "12.5km"
        assert "duration_text" in data["data"]  # "약 30분"
        assert "path" in data["data"]

    def test_search_route_with_waypoints_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        route_search_with_waypoints_request: dict,
    ) -> None:
        """TC-R-002: 경유지 포함 검색 성공"""
        with patch(
            "src.modules.routes.service.search_route_from_naver"
        ) as mock_naver:
            mock_naver.return_value = {
                "total_distance_m": 15000,
                "total_duration_s": 2400,
                "path": [
                    {"lat": 37.5547, "lng": 126.9706},
                    {"lat": 37.5636, "lng": 126.9869},  # 경유지
                    {"lat": 37.4979, "lng": 127.0276},
                ],
            }

            response = auth_client.post(
                "/routes/search", json=route_search_with_waypoints_request
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_distance_m"] == 15000

    def test_search_route_with_option_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        route_search_request: dict,
    ) -> None:
        """TC-R-003: 옵션 변경 검색 성공"""
        route_search_request["option"] = "trafast"  # 빠른길

        with patch(
            "src.modules.routes.service.search_route_from_naver"
        ) as mock_naver:
            mock_naver.return_value = {
                "total_distance_m": 14000,  # 거리는 더 길지만
                "total_duration_s": 1500,  # 시간은 더 짧음
                "path": [
                    {"lat": 37.5547, "lng": 126.9706},
                    {"lat": 37.4979, "lng": 127.0276},
                ],
            }

            response = auth_client.post("/routes/search", json=route_search_request)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_duration_s"] == 1500

    def test_search_route_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        route_search_request: dict,
    ) -> None:
        """TC-R-101: 경로 없음 -> 404"""
        with patch(
            "src.modules.routes.service.search_route_from_naver"
        ) as mock_naver:
            mock_naver.side_effect = Exception("Route not found")

            response = auth_client.post("/routes/search", json=route_search_request)

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "ROUTE_NOT_FOUND"

    def test_search_route_invalid_coordinates(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-R-102: 잘못된 좌표 (범위 초과) -> 400"""
        invalid_request = {
            "start": {
                "name": "잘못된 위치",
                "lat": 200,  # 유효 범위: -90 ~ 90
                "lng": 126.9706,
            },
            "end": {
                "name": "강남역",
                "lat": 37.4979,
                "lng": 127.0276,
            },
            "option": "traoptimal",
        }

        response = auth_client.post("/routes/search", json=invalid_request)

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "VALIDATION_FAILED"

    def test_search_route_too_many_waypoints(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        route_search_too_many_waypoints_request: dict,
    ) -> None:
        """TC-R-103: 경유지 초과 (6개) -> 400"""
        response = auth_client.post(
            "/routes/search", json=route_search_too_many_waypoints_request
        )

        assert response.status_code == 422
        data = response.json()
        # 경유지 최대 5개 제한


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
