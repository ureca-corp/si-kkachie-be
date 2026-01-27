"""phrases 도메인 컨트롤러 테스트

SPEC 기반 테스트 케이스:
- TC-P-001: 전체 문장 조회
- TC-P-002: 카테고리별 조회
- TC-P-003: 미션 단계별 조회
- TC-P-004: 문장 사용 기록
- TC-P-101: 없는 문장 사용
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.missions.models import MissionStep
from src.modules.phrases.models import Phrase, PhraseStepMapping
from src.modules.profiles.models import Profile


class TestListPhrases:
    """GET /phrases 테스트"""

    def test_list_phrases_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        greeting_phrase: Phrase,
        request_phrase: Phrase,
        thanks_phrase: Phrase,
    ) -> None:
        """TC-P-001: 전체 문장 조회 성공"""
        response = auth_client.get("/phrases")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "조회에 성공했어요"
        assert len(data["data"]) >= 3

        # 응답 구조 확인
        phrase = data["data"][0]
        assert "id" in phrase
        assert "text_ko" in phrase
        assert "text_en" in phrase
        assert "category" in phrase
        assert "usage_count" in phrase

    def test_list_phrases_filter_by_category(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        greeting_phrase: Phrase,
        request_phrase: Phrase,
    ) -> None:
        """TC-P-002: 카테고리별 조회 성공"""
        response = auth_client.get("/phrases?category=greeting")

        assert response.status_code == 200
        data = response.json()
        for phrase in data["data"]:
            assert phrase["category"] == "greeting"

    def test_list_phrases_filter_by_mission_step(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        request_phrase: Phrase,
        taxi_mission_steps: list[MissionStep],
        phrase_step_mapping: PhraseStepMapping,
    ) -> None:
        """TC-P-003: 미션 단계별 조회 성공"""
        step_id = taxi_mission_steps[0].id

        response = auth_client.get(f"/phrases?mission_step_id={step_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1
        # 해당 단계에 매핑된 문장만 반환

    def test_list_phrases_excludes_inactive(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        greeting_phrase: Phrase,
        inactive_phrase: Phrase,
    ) -> None:
        """비활성 문장은 목록에서 제외"""
        response = auth_client.get("/phrases")

        assert response.status_code == 200
        data = response.json()
        phrase_ids = [p["id"] for p in data["data"]]
        assert str(inactive_phrase.id) not in phrase_ids

    def test_list_phrases_empty(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """문장이 없을 때 빈 목록"""
        response = auth_client.get("/phrases")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []

    def test_list_phrases_sorted_by_usage(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        greeting_phrase: Phrase,  # usage_count=100
        request_phrase: Phrase,  # usage_count=50
        thanks_phrase: Phrase,  # usage_count=200
    ) -> None:
        """사용량 기준 정렬 확인"""
        response = auth_client.get("/phrases")

        assert response.status_code == 200
        data = response.json()

        # usage_count 내림차순 정렬 확인
        usage_counts = [p["usage_count"] for p in data["data"]]
        assert usage_counts == sorted(usage_counts, reverse=True)


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
