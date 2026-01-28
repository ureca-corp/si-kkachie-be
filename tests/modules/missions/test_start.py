"""POST /missions/{id}/start 테스트

SPEC 기반 테스트 케이스:
- TC-M-003: 미션 시작
- TC-M-102: 이미 시작한 미션
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from src.modules.missions._models import (
    MissionProgress,
    MissionStep,
    MissionTemplate,
)
from src.modules.profiles._models import Profile


class TestStartMission:
    """POST /missions/{id}/start 테스트"""

    def test_start_mission_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        taxi_mission_steps: list[MissionStep],
    ) -> None:
        """TC-M-003: 미션 시작 성공"""
        response = auth_client.post(f"/missions/{taxi_mission_template.id}/start")

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "미션을 시작했어요"
        assert data["data"]["status"] == "in_progress"
        assert data["data"]["current_step"] == 1
        assert "started_at" in data["data"]

    def test_start_mission_already_started(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        mission_progress_in_progress: MissionProgress,
    ) -> None:
        """TC-M-102: 이미 시작한 미션 -> 409"""
        response = auth_client.post(f"/missions/{taxi_mission_template.id}/start")

        assert response.status_code == 409
        data = response.json()
        assert data["status"] == "ERROR_MISSION_ALREADY_STARTED"

    def test_start_mission_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """존재하지 않는 미션 시작 -> 404"""
        fake_id = uuid4()
        response = auth_client.post(f"/missions/{fake_id}/start")

        assert response.status_code == 404
