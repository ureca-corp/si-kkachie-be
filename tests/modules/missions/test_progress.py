"""PATCH /missions/{id}/progress 테스트

SPEC 기반 테스트 케이스:
- TC-M-004: 단계 완료
- TC-M-103: 시작 전 단계 완료
"""

from fastapi.testclient import TestClient

from src.modules.missions._models import (
    MissionProgress,
    MissionStep,
    MissionTemplate,
)
from src.modules.profiles._models import Profile


class TestUpdateProgress:
    """PATCH /missions/{id}/progress 테스트"""

    def test_update_progress_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        taxi_mission_steps: list[MissionStep],
        mission_progress_in_progress: MissionProgress,
    ) -> None:
        """TC-M-004: 단계 완료 처리 성공"""
        step_id = taxi_mission_steps[1].id  # 두 번째 단계

        response = auth_client.patch(
            f"/missions/{taxi_mission_template.id}/progress",
            json={
                "step_id": str(step_id),
                "is_completed": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "단계를 완료했어요"
        assert data["data"]["current_step"] == 3  # 다음 단계로 이동
        assert data["data"]["completed_steps"] == 2

    def test_update_progress_not_started(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        taxi_mission_steps: list[MissionStep],
    ) -> None:
        """TC-M-103: 시작 전 단계 완료 -> 400"""
        step_id = taxi_mission_steps[0].id

        response = auth_client.patch(
            f"/missions/{taxi_mission_template.id}/progress",
            json={
                "step_id": str(step_id),
                "is_completed": True,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "ERROR_MISSION_NOT_STARTED"
