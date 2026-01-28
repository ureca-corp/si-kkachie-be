"""DELETE /translations/{id} 테스트

SPEC 기반 테스트 케이스:
- TC-T-005: 기록 삭제
- TC-T-104: 타인 기록 삭제
"""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.profiles import Profile
from src.modules.translations._models import Translation


class TestDeleteTranslation:
    """DELETE /translations/{id} 테스트"""

    def test_delete_translation_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_translation: Translation,
    ) -> None:
        """TC-T-005: 기록 삭제 성공"""
        response = auth_client.delete(f"/translations/{created_translation.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "번역 기록이 삭제됐어요"

    def test_delete_translation_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """존재하지 않는 기록 삭제 -> 404"""
        fake_id = uuid4()
        response = auth_client.delete(f"/translations/{fake_id}")

        assert response.status_code == 404

    def test_delete_translation_other_user(
        self,
        auth_client: TestClient,
        session: Session,
        test_profile: Profile,
    ) -> None:
        """TC-T-104: 타인 기록 삭제 시도 -> 404"""
        # 다른 사용자의 번역 기록 생성
        other_profile = Profile(
            id=uuid4(),
            user_id=uuid4(),
            display_name="OtherUser",
            preferred_language="en",
        )
        session.add(other_profile)
        session.commit()

        other_translation = Translation(
            id=uuid4(),
            profile_id=other_profile.id,
            source_text="Test",
            translated_text="테스트",
            source_lang="en",
            target_lang="ko",
            translation_type="text",
        )
        session.add(other_translation)
        session.commit()

        # 다른 사용자의 기록 삭제 시도
        response = auth_client.delete(f"/translations/{other_translation.id}")

        assert response.status_code == 404
