"""search 테스트

GET /locations/search
- TC-L-005: 장소 검색 성공
- TC-L-006: 검색 결과 없음
- TC-L-007: 현재 위치 포함 검색 (거리 계산)
"""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from src.modules.profiles._models import Profile


class TestPlaceSearch:
    """GET /locations/search 테스트"""

    def test_search_places_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        place_search_response: dict,
    ) -> None:
        """TC-L-005: 장소 검색 성공"""
        mock_provider = MagicMock()
        mock_provider.search_places = AsyncMock(return_value=place_search_response)

        with patch(
            "src.modules.locations.search.get_naver_provider",
            return_value=mock_provider,
        ):
            response = auth_client.get(
                "/locations/search",
                params={"query": "강남역"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "검색에 성공했어요"
        assert len(data["data"]) == 2

        # 첫 번째 결과 확인
        first = data["data"][0]
        assert first["name"] == "강남역"  # HTML 태그 제거됨
        assert first["category"] == "지하철역"
        assert first["address"] == "서울특별시 강남구 역삼동 858"
        assert first["road_address"] == "서울특별시 강남구 강남대로 396"
        assert first["distance"] is None  # 위치 미제공

    def test_search_places_empty(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        place_search_empty_response: dict,
    ) -> None:
        """TC-L-006: 검색 결과 없음"""
        mock_provider = MagicMock()
        mock_provider.search_places = AsyncMock(return_value=place_search_empty_response)

        with patch(
            "src.modules.locations.search.get_naver_provider",
            return_value=mock_provider,
        ):
            response = auth_client.get(
                "/locations/search",
                params={"query": "존재하지않는장소12345"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["data"] == []

    def test_search_places_with_location(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        place_search_response: dict,
    ) -> None:
        """TC-L-007: 현재 위치 포함 검색 (거리 계산)"""
        mock_provider = MagicMock()
        mock_provider.search_places = AsyncMock(return_value=place_search_response)

        with patch(
            "src.modules.locations.search.get_naver_provider",
            return_value=mock_provider,
        ):
            # 거리 계산 모킹 (PostGIS 없는 SQLite에서도 동작)
            with patch(
                "src.modules.locations.search.calculate_distance"
            ) as mock_distance:
                mock_distance.return_value = 500  # 500m

                response = auth_client.get(
                    "/locations/search",
                    params={
                        "query": "강남역",
                        "lat": 37.4979,
                        "lng": 127.0276,
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

        # 거리 계산됨
        first = data["data"][0]
        assert first["distance"] == 500

    def test_search_places_unauthorized(
        self,
        client: TestClient,
    ) -> None:
        """인증 없이 장소 검색 호출"""
        response = client.get(
            "/locations/search",
            params={"query": "강남역"},
        )

        assert response.status_code == 401

    def test_search_places_invalid_query(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """빈 검색어 (최소 1자)"""
        response = auth_client.get(
            "/locations/search",
            params={"query": ""},
        )

        assert response.status_code == 422

    def test_search_places_external_service_error(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """외부 서비스 오류"""
        mock_provider = MagicMock()
        mock_provider.search_places = AsyncMock(side_effect=Exception("API 오류"))

        with patch(
            "src.modules.locations.search.get_naver_provider",
            return_value=mock_provider,
        ):
            response = auth_client.get(
                "/locations/search",
                params={"query": "강남역"},
            )

        assert response.status_code == 502
        data = response.json()
        assert data["status"] == "EXTERNAL_SERVICE_ERROR"
