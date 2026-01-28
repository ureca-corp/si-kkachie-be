"""reverse_geocode 테스트

GET /locations/reverse-geocode
- TC-L-001: 좌표 → 주소 변환 성공
- TC-L-002: 좌표에 해당하는 주소 없음
- TC-L-003: 잘못된 좌표값
- TC-L-004: 인증 없이 호출
- TC-L-005: 외부 서비스 오류
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.modules.profiles._models import Profile


class TestReverseGeocode:
    """GET /locations/reverse-geocode 테스트"""

    def test_reverse_geocode_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        reverse_geocode_response: dict,
    ) -> None:
        """TC-L-001: 좌표 → 주소 변환 성공"""
        with patch(
            "src.modules.locations.reverse_geocode.naver_provider.reverse_geocode",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.return_value = reverse_geocode_response

            response = auth_client.get(
                "/locations/reverse-geocode",
                params={"lat": 37.5665, "lng": 126.9780},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "위치 정보를 가져왔어요"
        assert data["data"]["name"] == "서울시청"
        assert data["data"]["road_address"] == "서울특별시 중구 태평로1가 세종대로 110"
        assert data["data"]["address"] == "서울특별시 중구 태평로1가 31"
        assert data["data"]["lat"] == 37.5665
        assert data["data"]["lng"] == 126.9780

    def test_reverse_geocode_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        reverse_geocode_not_found_response: dict,
    ) -> None:
        """TC-L-002: 좌표에 해당하는 주소 없음"""
        with patch(
            "src.modules.locations.reverse_geocode.naver_provider.reverse_geocode",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.return_value = reverse_geocode_not_found_response

            response = auth_client.get(
                "/locations/reverse-geocode",
                params={"lat": 0.0, "lng": 0.0},  # 바다 한가운데
            )

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "LOCATION_NOT_FOUND"

    def test_reverse_geocode_invalid_coordinates(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-L-003: 잘못된 좌표값 (범위 초과)"""
        response = auth_client.get(
            "/locations/reverse-geocode",
            params={"lat": 999, "lng": 126.9780},  # lat 범위 초과
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "VALIDATION_FAILED"

    def test_reverse_geocode_unauthorized(
        self,
        client: TestClient,
    ) -> None:
        """TC-L-004: 인증 없이 호출"""
        response = client.get(
            "/locations/reverse-geocode",
            params={"lat": 37.5665, "lng": 126.9780},
        )

        assert response.status_code == 401

    def test_reverse_geocode_external_service_error(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-L-005: 외부 서비스 오류"""
        with patch(
            "src.modules.locations.reverse_geocode.naver_provider.reverse_geocode",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.side_effect = Exception("API 오류")

            response = auth_client.get(
                "/locations/reverse-geocode",
                params={"lat": 37.5665, "lng": 126.9780},
            )

        assert response.status_code == 502
        data = response.json()
        assert data["status"] == "EXTERNAL_SERVICE_ERROR"
