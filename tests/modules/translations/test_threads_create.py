"""POST /translation/threads 테스트

스레드 생성 API 테스트 케이스:
- TC-TH-001: 스레드 생성 성공
- TC-TH-002: 유효하지 않은 카테고리 조합
- TC-TH-003: 존재하지 않는 1차 카테고리
- TC-TH-004: 존재하지 않는 2차 카테고리
"""

from fastapi.testclient import TestClient

from src.modules.profiles import Profile
from src.modules.translations._models import (
    TranslationCategoryMapping,
    TranslationPrimaryCategory,
    TranslationSubCategory,
)


class TestCreateThread:
    """POST /translation/threads 테스트"""

    def test_create_thread_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TH-001: 스레드 생성 성공"""
        response = auth_client.post(
            "/translation/threads",
            json={
                "primary_category": "FD6",
                "sub_category": "ordering",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "번역 스레드를 생성했어요"
        assert "id" in data["data"]
        assert data["data"]["primary_category"] == "FD6"
        assert data["data"]["sub_category"] == "ordering"

    def test_create_thread_invalid_mapping(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TH-002: 유효하지 않은 카테고리 조합"""
        # GEN(일반) 카테고리에 ordering은 매핑되어 있지 않음
        response = auth_client.post(
            "/translation/threads",
            json={
                "primary_category": "GEN",
                "sub_category": "ordering",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "INVALID_CATEGORY"

    def test_create_thread_invalid_primary_category(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TH-003: 존재하지 않는 1차 카테고리"""
        response = auth_client.post(
            "/translation/threads",
            json={
                "primary_category": "INVALID",
                "sub_category": "ordering",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "INVALID_CATEGORY"

    def test_create_thread_invalid_sub_category(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TH-004: 존재하지 않는 2차 카테고리"""
        response = auth_client.post(
            "/translation/threads",
            json={
                "primary_category": "FD6",
                "sub_category": "invalid_sub",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "INVALID_CATEGORY"
