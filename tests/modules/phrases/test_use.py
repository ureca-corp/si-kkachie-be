"""POST /phrases/{id}/use 테스트

SPEC 기반 테스트 케이스:
- TC-P-004: 문장 사용 기록
- TC-P-101: 없는 문장 사용
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from src.modules.phrases._models import Phrase
from src.modules.profiles._models import Profile


class TestUsePhrase:
    """POST /phrases/{id}/use 테스트"""

    def test_use_phrase_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        greeting_phrase: Phrase,
    ) -> None:
        """TC-P-004: 문장 사용 기록 성공"""
        initial_count = greeting_phrase.usage_count

        response = auth_client.post(f"/phrases/{greeting_phrase.id}/use")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "사용이 기록됐어요"
        assert data["data"]["id"] == str(greeting_phrase.id)
        assert data["data"]["usage_count"] == initial_count + 1

    def test_use_phrase_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-P-101: 없는 문장 사용 -> 404"""
        fake_id = uuid4()

        response = auth_client.post(f"/phrases/{fake_id}/use")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "PHRASE_NOT_FOUND"

    def test_use_phrase_multiple_times(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        greeting_phrase: Phrase,
    ) -> None:
        """문장 여러 번 사용"""
        initial_count = greeting_phrase.usage_count

        # 3번 사용
        for i in range(3):
            response = auth_client.post(f"/phrases/{greeting_phrase.id}/use")
            assert response.status_code == 200
            assert response.json()["data"]["usage_count"] == initial_count + i + 1
