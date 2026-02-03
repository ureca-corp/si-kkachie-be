"""경로 검색 테스트

POST /routes/search

SPEC 기반 테스트 케이스:
- TC-R-001: 기본 경로 검색
- TC-R-002: 경유지 포함 검색
- TC-R-003: 옵션 변경 검색
- TC-R-101: 경로 없음
- TC-R-102: 잘못된 좌표
- TC-R-103: 경유지 초과
"""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from src.modules.profiles import Profile


class TestSearchRoute:
    """POST /routes/search 테스트"""

    def test_search_route_basic_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        route_search_request: dict,
    ) -> None:
        """TC-R-001: 기본 경로 검색 성공"""
        mock_provider = MagicMock()
        mock_provider.directions = AsyncMock(
            return_value={
                "total_distance_m": 12500,
                "total_duration_s": 1800,
                "path": [
                    [126.9706, 37.5547],
                    [126.9800, 37.5500],
                    [127.0276, 37.4979],
                ],
            }
        )

        with patch(
            "src.modules.routes.search.get_kakao_provider",
            return_value=mock_provider,
        ):
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
        mock_provider = MagicMock()
        mock_provider.directions = AsyncMock(
            return_value={
                "total_distance_m": 15000,
                "total_duration_s": 2400,
                "path": [
                    [126.9706, 37.5547],
                    [126.9869, 37.5636],  # 경유지
                    [127.0276, 37.4979],
                ],
            }
        )

        with patch(
            "src.modules.routes.search.get_kakao_provider",
            return_value=mock_provider,
        ):
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

        mock_provider = MagicMock()
        mock_provider.directions = AsyncMock(
            return_value={
                "total_distance_m": 14000,  # 거리는 더 길지만
                "total_duration_s": 1500,  # 시간은 더 짧음
                "path": [
                    [126.9706, 37.5547],
                    [127.0276, 37.4979],
                ],
            }
        )

        with patch(
            "src.modules.routes.search.get_kakao_provider",
            return_value=mock_provider,
        ):
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
        mock_provider = MagicMock()
        mock_provider.directions = AsyncMock(side_effect=Exception("Route not found"))

        with patch(
            "src.modules.routes.search.get_kakao_provider",
            return_value=mock_provider,
        ):
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
        # 경유지 최대 5개 제한
