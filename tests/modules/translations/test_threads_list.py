"""GET /translation/threads 테스트

스레드 목록 조회 API 테스트 케이스:
- TC-TH-005: 스레드 목록 조회 성공
- TC-TH-006: 페이지네이션 동작
- TC-TH-007: 삭제된 스레드 제외
- TC-TH-008: 빈 목록 조회
"""

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.profiles import Profile
from src.modules.translations._models import (
    TranslationCategoryMapping,
    TranslationPrimaryCategory,
    TranslationSubCategory,
    TranslationThread,
)


class TestListThreads:
    """GET /translation/threads 테스트"""

    def test_list_threads_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_thread: TranslationThread,
    ) -> None:
        """TC-TH-005: 스레드 목록 조회 성공"""
        response = auth_client.get("/translation/threads")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "스레드 목록을 조회했어요"
        assert "items" in data["data"]
        assert "pagination" in data["data"]
        assert len(data["data"]["items"]) >= 1

    def test_list_threads_with_pagination(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_thread: TranslationThread,
    ) -> None:
        """TC-TH-006: 페이지네이션 동작"""
        response = auth_client.get("/translation/threads?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 10

    def test_list_threads_excludes_deleted(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        session: Session,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TH-007: 삭제된 스레드 제외"""
        from uuid import uuid4

        # 삭제된 스레드 생성
        deleted_thread = TranslationThread(
            id=uuid4(),
            profile_id=test_profile.id,
            primary_category="FD6",
            sub_category="ordering",
            created_at=datetime.now(UTC),
            deleted_at=datetime.now(UTC),  # 삭제됨
        )
        session.add(deleted_thread)
        session.commit()

        response = auth_client.get("/translation/threads")

        assert response.status_code == 200
        data = response.json()
        # 삭제된 스레드는 목록에 포함되지 않아야 함
        thread_ids = [item["id"] for item in data["data"]["items"]]
        assert str(deleted_thread.id) not in thread_ids

    def test_list_threads_empty(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        seeded_categories: tuple[
            list[TranslationPrimaryCategory],
            list[TranslationSubCategory],
            list[TranslationCategoryMapping],
        ],
    ) -> None:
        """TC-TH-008: 빈 목록 조회"""
        response = auth_client.get("/translation/threads")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["items"] == []
