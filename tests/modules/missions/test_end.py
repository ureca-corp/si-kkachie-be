"""POST /missions/{id}/end 테스트

SPEC 기반 테스트 케이스:
- TC-M-005: 미션 종료 (해결)
- TC-M-006: 미션 종료 (부분해결)
- TC-M-007: 미션 종료 (미해결)
- TC-M-104: 잘못된 결과값
"""

from fastapi.testclient import TestClient

from src.modules.missions._models import (
    MissionProgress,
    MissionStep,
    MissionTemplate,
)
from src.modules.profiles._models import Profile


class TestEndMission:
    """POST /missions/{id}/end 테스트"""

    def test_end_mission_resolved_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        mission_progress_in_progress: MissionProgress,
        end_mission_request_resolved: dict,
    ) -> None:
        """TC-M-005: 미션 종료 (해결) 성공"""
        response = auth_client.post(
            f"/missions/{taxi_mission_template.id}/end",
            json=end_mission_request_resolved,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "미션을 종료했어요"
        assert data["data"]["status"] == "ended"
        assert data["data"]["result"] == "resolved"
        assert "ended_at" in data["data"]
        assert "duration_minutes" in data["data"]

    def test_end_mission_partially_resolved_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        mission_progress_in_progress: MissionProgress,
        end_mission_request_partially_resolved: dict,
    ) -> None:
        """TC-M-006: 미션 종료 (부분해결) 성공"""
        response = auth_client.post(
            f"/missions/{taxi_mission_template.id}/end",
            json=end_mission_request_partially_resolved,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["result"] == "partially_resolved"

    def test_end_mission_unresolved_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        mission_progress_in_progress: MissionProgress,
        end_mission_request_unresolved: dict,
    ) -> None:
        """TC-M-007: 미션 종료 (미해결) 성공"""
        response = auth_client.post(
            f"/missions/{taxi_mission_template.id}/end",
            json=end_mission_request_unresolved,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["result"] == "unresolved"

    def test_end_mission_invalid_result(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        mission_progress_in_progress: MissionProgress,
    ) -> None:
        """TC-M-104: 잘못된 결과값 -> 400"""
        response = auth_client.post(
            f"/missions/{taxi_mission_template.id}/end",
            json={"result": "invalid_result"},
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "VALIDATION_FAILED"

    def test_end_mission_not_started(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        taxi_mission_steps: list[MissionStep],
    ) -> None:
        """시작하지 않은 미션 종료 -> 400"""
        response = auth_client.post(
            f"/missions/{taxi_mission_template.id}/end",
            json={"result": "resolved"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "ERROR_MISSION_NOT_STARTED"
