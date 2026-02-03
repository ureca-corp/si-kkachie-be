"""GET /translation/categories 테스트

카테고리 목록 조회 API 테스트 케이스:
- TC-TC-001: 전체 카테고리 목록 조회 성공
- TC-TC-002: Primary 카테고리 목록 포함 확인
- TC-TC-003: Sub 카테고리 목록 포함 확인
- TC-TC-004: 카테고리 매핑 포함 확인
"""

from fastapi.testclient import TestClient

from src.modules.profiles import Profile
from src.modules.translations._models import (
    TranslationCategoryMapping,
    TranslationPrimaryCategory,
    TranslationSubCategory,
)


class TestListCategories:
    """GET /translation/categories 테스트"""

    def test_get_categories_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,  # auth_client가 프로필을 찾을 수 있도록
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TC-001: 전체 카테고리 목록 조회 성공"""
        response = auth_client.get("/translation/categories")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "카테고리 목록을 조회했어요"
        assert "primary_categories" in data["data"]
        assert "sub_categories" in data["data"]
        assert "mappings" in data["data"]

    def test_get_categories_primary_list(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TC-002: Primary 카테고리 목록 포함 확인"""
        response = auth_client.get("/translation/categories")

        assert response.status_code == 200
        data = response.json()
        primary = data["data"]["primary_categories"]
        assert len(primary) > 0

        # 첫 번째 카테고리 구조 확인
        first = primary[0]
        assert "code" in first
        assert "name_ko" in first
        assert "name_en" in first

    def test_get_categories_sub_list(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TC-003: Sub 카테고리 목록 포함 확인"""
        response = auth_client.get("/translation/categories")

        assert response.status_code == 200
        data = response.json()
        sub = data["data"]["sub_categories"]
        assert len(sub) > 0

        # 첫 번째 서브 카테고리 구조 확인
        first = sub[0]
        assert "code" in first
        assert "name_ko" in first
        assert "name_en" in first

    def test_get_categories_mappings(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TC-004: 카테고리 매핑 포함 확인"""
        response = auth_client.get("/translation/categories")

        assert response.status_code == 200
        data = response.json()
        mappings = data["data"]["mappings"]

        # mappings는 dict[primary_code, list[sub_code]] 형태
        assert isinstance(mappings, dict)
        assert len(mappings) > 0

        # FD6 카테고리의 서브 카테고리 확인
        assert "FD6" in mappings
        assert isinstance(mappings["FD6"], list)
        assert len(mappings["FD6"]) > 0

    def test_get_categories_ordered_by_display_order(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """카테고리가 display_order 순으로 정렬되어 있는지 확인"""
        response = auth_client.get("/translation/categories")

        assert response.status_code == 200
        data = response.json()
        primary = data["data"]["primary_categories"]

        # display_order 순서로 정렬되어 있어야 함
        # FD6(1) -> CE7(2) -> HP8(3) -> ...
        if len(primary) >= 2:
            # 첫 번째가 FD6 (display_order=1)
            assert primary[0]["code"] == "FD6"
