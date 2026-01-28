"""GET /translations 테스트

SPEC 기반 테스트 케이스:
- TC-T-004: 히스토리 조회
"""

from fastapi.testclient import TestClient

from src.modules.profiles import Profile
from src.modules.translations._models import Translation


class TestListTranslations:
    """GET /translations 테스트"""

    def test_get_translations_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_translation: Translation,
    ) -> None:
        """TC-T-004: 히스토리 조회 성공"""
        response = auth_client.get("/translations")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "조회에 성공했어요"
        assert "items" in data["data"]
        assert "pagination" in data["data"]
        assert len(data["data"]["items"]) >= 1

    def test_get_translations_with_pagination(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_translation: Translation,
    ) -> None:
        """페이지네이션 테스트"""
        response = auth_client.get("/translations?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 10

    def test_get_translations_filter_by_type(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_translation: Translation,
        voice_translation: Translation,
    ) -> None:
        """타입별 필터링 테스트"""
        response = auth_client.get("/translations?type=text")

        assert response.status_code == 200
        data = response.json()
        for item in data["data"]["items"]:
            assert item["translation_type"] == "text"

    def test_get_translations_empty(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """빈 목록 조회"""
        response = auth_client.get("/translations")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["items"] == []
