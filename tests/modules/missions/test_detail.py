"""GET /missions/{id} 테스트

SPEC 기반 테스트 케이스:
- TC-M-002: 미션 상세 조회
- TC-M-101: 없는 미션 조회
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from src.modules.missions._models import (
    MissionStep,
    MissionTemplate,
)
from src.modules.profiles._models import Profile


class TestGetMission:
    """GET /missions/{id} 테스트"""

    def test_get_mission_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        taxi_mission_steps: list[MissionStep],
    ) -> None:
        """TC-M-002: 미션 상세 조회 성공"""
        response = auth_client.get(f"/missions/{taxi_mission_template.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["data"]["id"] == str(taxi_mission_template.id)
        assert data["data"]["mission_type"] == "taxi"
        assert "steps" in data["data"]
        assert len(data["data"]["steps"]) == 5

    def test_get_mission_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-M-101: 없는 미션 조회 -> 404"""
        fake_id = uuid4()
        response = auth_client.get(f"/missions/{fake_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "MISSION_NOT_FOUND"
