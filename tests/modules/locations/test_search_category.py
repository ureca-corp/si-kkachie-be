"""search_category 테스트

GET /locations/search/category
- TC-L-008: 카테고리별 장소 검색 성공
- TC-L-009: 검색 결과 없음
- TC-L-010: 페이지네이션
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.modules.profiles._models import Profile


class TestPlaceCategorySearch:
    """GET /locations/search/category 테스트"""

    def test_search_category_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        category_search_response: dict,
    ) -> None:
        """TC-L-008: 카테고리별 장소 검색 성공"""
        with patch(
            "src.modules.locations.search_category.kakao_provider.search_by_category",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.return_value = category_search_response

            response = auth_client.get(
                "/locations/search/category",
                params={
                    "category": "CE7",  # 카페
                    "lat": 37.4979,
                    "lng": 127.0276,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "주변 장소를 찾았어요"

        result = data["data"]
        assert result["total_count"] == 45
        assert result["page"] == 1
        assert result["is_end"] is False
        assert len(result["places"]) == 2

        # 첫 번째 결과 확인
        first = result["places"][0]
        assert first["id"] == "8569385"
        assert first["name"] == "스타벅스 강남역점"
        assert first["category"] == "카페"
        assert first["distance_m"] == 150

    def test_search_category_empty(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        category_search_empty_response: dict,
    ) -> None:
        """TC-L-009: 검색 결과 없음"""
        with patch(
            "src.modules.locations.search_category.kakao_provider.search_by_category",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.return_value = category_search_empty_response

            response = auth_client.get(
                "/locations/search/category",
                params={
                    "category": "CE7",
                    "lat": 37.0,
                    "lng": 127.0,
                    "radius": 100,  # 좁은 반경
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["data"]["total_count"] == 0
        assert data["data"]["places"] == []

    def test_search_category_with_pagination(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        category_search_response: dict,
    ) -> None:
        """TC-L-010: 페이지네이션"""
        with patch(
            "src.modules.locations.search_category.kakao_provider.search_by_category",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.return_value = category_search_response

            response = auth_client.get(
                "/locations/search/category",
                params={
                    "category": "CE7",
                    "lat": 37.4979,
                    "lng": 127.0276,
                    "page": 2,
                    "size": 10,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 2

        # API 호출 파라미터 확인
        mock_api.assert_called_once_with(
            category="CE7",
            lng=127.0276,
            lat=37.4979,
            radius=1000,
            page=2,
            size=10,
            sort="distance",
        )

    def test_search_category_with_custom_radius(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        category_search_response: dict,
    ) -> None:
        """커스텀 반경 설정"""
        with patch(
            "src.modules.locations.search_category.kakao_provider.search_by_category",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.return_value = category_search_response

            response = auth_client.get(
                "/locations/search/category",
                params={
                    "category": "MT1",  # 대형마트
                    "lat": 37.4979,
                    "lng": 127.0276,
                    "radius": 5000,
                },
            )

        assert response.status_code == 200

        # 반경 5000m로 호출 확인
        mock_api.assert_called_once()
        call_kwargs = mock_api.call_args.kwargs
        assert call_kwargs["radius"] == 5000

    def test_search_category_unauthorized(
        self,
        client: TestClient,
    ) -> None:
        """인증 없이 카테고리 검색 호출"""
        response = client.get(
            "/locations/search/category",
            params={
                "category": "CE7",
                "lat": 37.4979,
                "lng": 127.0276,
            },
        )

        assert response.status_code == 401

    def test_search_category_missing_params(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """필수 파라미터 누락"""
        # category 누락
        response = auth_client.get(
            "/locations/search/category",
            params={
                "lat": 37.4979,
                "lng": 127.0276,
            },
        )
        assert response.status_code == 422

        # lat 누락
        response = auth_client.get(
            "/locations/search/category",
            params={
                "category": "CE7",
                "lng": 127.0276,
            },
        )
        assert response.status_code == 422

        # lng 누락
        response = auth_client.get(
            "/locations/search/category",
            params={
                "category": "CE7",
                "lat": 37.4979,
            },
        )
        assert response.status_code == 422

    def test_search_category_invalid_lat_lng(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """잘못된 좌표 범위"""
        # 위도 범위 초과
        response = auth_client.get(
            "/locations/search/category",
            params={
                "category": "CE7",
                "lat": 91,  # 최대 90
                "lng": 127.0276,
            },
        )
        assert response.status_code == 422

        # 경도 범위 초과
        response = auth_client.get(
            "/locations/search/category",
            params={
                "category": "CE7",
                "lat": 37.4979,
                "lng": 181,  # 최대 180
            },
        )
        assert response.status_code == 422

    def test_search_category_invalid_radius(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """잘못된 반경 범위"""
        # 반경 최대값 초과
        response = auth_client.get(
            "/locations/search/category",
            params={
                "category": "CE7",
                "lat": 37.4979,
                "lng": 127.0276,
                "radius": 25000,  # 최대 20000
            },
        )
        assert response.status_code == 422

    def test_search_category_external_service_error(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """외부 서비스 오류"""
        with patch(
            "src.modules.locations.search_category.kakao_provider.search_by_category",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.side_effect = Exception("Kakao API 오류")

            response = auth_client.get(
                "/locations/search/category",
                params={
                    "category": "CE7",
                    "lat": 37.4979,
                    "lng": 127.0276,
                },
            )

        assert response.status_code == 502
        data = response.json()
        assert data["status"] == "EXTERNAL_SERVICE_ERROR"
