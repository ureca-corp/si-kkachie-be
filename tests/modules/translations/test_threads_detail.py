"""GET /translation/threads/{thread_id} 테스트

스레드 상세 조회 API 테스트 케이스:
- TC-TH-009: 스레드 상세 조회 성공
- TC-TH-010: 번역 기록 포함
- TC-TH-011: 존재하지 않는 스레드
- TC-TH-012: 다른 사용자의 스레드 조회 불가
"""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.profiles import Profile
from src.modules.translations._models import (
    Translation,
    TranslationThread,
)


class TestGetThread:
    """GET /translation/threads/{thread_id} 테스트"""

    def test_get_thread_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_thread: TranslationThread,
    ) -> None:
        """TC-TH-009: 스레드 상세 조회 성공"""
        response = auth_client.get(f"/translation/threads/{created_thread.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "스레드를 조회했어요"
        assert data["data"]["id"] == str(created_thread.id)
        assert data["data"]["primary_category"] == "FD6"
        assert data["data"]["sub_category"] == "ordering"
        assert "translations" in data["data"]

    def test_get_thread_with_translations(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        thread_with_translations: tuple[TranslationThread, list[Translation]],
    ) -> None:
        """TC-TH-010: 번역 기록 포함"""
        thread, translations = thread_with_translations

        response = auth_client.get(f"/translation/threads/{thread.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["translations"]) == len(translations)

    def test_get_thread_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-TH-011: 존재하지 않는 스레드"""
        fake_id = uuid4()
        response = auth_client.get(f"/translation/threads/{fake_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "THREAD_NOT_FOUND"

    def test_get_thread_other_user(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        session: Session,
        seeded_categories: tuple,
    ) -> None:
        """TC-TH-012: 다른 사용자의 스레드 조회 불가"""
        from datetime import UTC, datetime

        # 다른 사용자 프로필 생성 (FK 제약 충족)
        from src.modules.profiles import Profile as ProfileModel

        other_profile = ProfileModel(
            id=uuid4(),
            user_id=uuid4(),
            display_name="OtherUser",
            preferred_language="en",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.add(other_profile)
        session.commit()

        # 다른 사용자의 스레드 생성
        other_thread = TranslationThread(
            id=uuid4(),
            profile_id=other_profile.id,
            primary_category="FD6",
            sub_category="ordering",
            created_at=datetime.now(UTC),
        )
        session.add(other_thread)
        session.commit()

        response = auth_client.get(f"/translation/threads/{other_thread.id}")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "THREAD_NOT_FOUND"
