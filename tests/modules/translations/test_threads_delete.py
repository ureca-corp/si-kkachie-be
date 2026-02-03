"""DELETE /translation/threads/{thread_id} 테스트

스레드 삭제 API 테스트 케이스:
- TC-TH-013: 스레드 삭제 성공 (soft delete)
- TC-TH-014: 존재하지 않는 스레드 삭제
- TC-TH-015: 다른 사용자의 스레드 삭제 불가
- TC-TH-016: 이미 삭제된 스레드 삭제
"""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.profiles import Profile
from src.modules.translations._models import (
    TranslationCategoryMapping,
    TranslationPrimaryCategory,
    TranslationSubCategory,
    TranslationThread,
)


class TestDeleteThread:
    """DELETE /translation/threads/{thread_id} 테스트"""

    def test_delete_thread_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_thread: TranslationThread,
        session: Session,
    ) -> None:
        """TC-TH-013: 스레드 삭제 성공 (soft delete)"""
        response = auth_client.delete(f"/translation/threads/{created_thread.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "스레드를 삭제했어요"

        # DB에서 soft delete 확인
        session.refresh(created_thread)
        assert created_thread.deleted_at is not None

    def test_delete_thread_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-TH-014: 존재하지 않는 스레드 삭제"""
        fake_id = uuid4()
        response = auth_client.delete(f"/translation/threads/{fake_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "THREAD_NOT_FOUND"

    def test_delete_thread_other_user(
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
        """TC-TH-015: 다른 사용자의 스레드 삭제 불가"""
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

        response = auth_client.delete(f"/translation/threads/{other_thread.id}")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "THREAD_NOT_FOUND"

    def test_delete_thread_already_deleted(
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
        """TC-TH-016: 이미 삭제된 스레드 삭제"""
        # 이미 삭제된 스레드 생성
        deleted_thread = TranslationThread(
            id=uuid4(),
            profile_id=test_profile.id,
            primary_category="FD6",
            sub_category="ordering",
            created_at=datetime.now(UTC),
            deleted_at=datetime.now(UTC),
        )
        session.add(deleted_thread)
        session.commit()

        response = auth_client.delete(f"/translation/threads/{deleted_thread.id}")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "THREAD_NOT_FOUND"
