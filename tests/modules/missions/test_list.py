"""GET /missions 테스트

SPEC 기반 테스트 케이스:
- TC-M-001: 미션 목록 조회
"""

from fastapi.testclient import TestClient

from src.modules.missions._models import (
    MissionProgress,
    MissionStep,
    MissionTemplate,
)
from src.modules.profiles._models import Profile


class TestListMissions:
    """GET /missions 테스트"""

    def test_list_missions_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        taxi_mission_steps: list[MissionStep],
    ) -> None:
        """TC-M-001: 미션 목록 조회 성공"""
        response = auth_client.get("/missions")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "조회에 성공했어요"
        assert len(data["data"]) >= 1

        mission = data["data"][0]
        assert "id" in mission
        assert "title" in mission
        assert "description" in mission
        assert "mission_type" in mission
        assert "estimated_duration_min" in mission
        assert "steps_count" in mission

    def test_list_missions_with_user_progress(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        taxi_mission_template: MissionTemplate,
        taxi_mission_steps: list[MissionStep],
        mission_progress_in_progress: MissionProgress,
    ) -> None:
        """미션 목록에 사용자 진행 상태 포함"""
        response = auth_client.get("/missions")

        assert response.status_code == 200
        data = response.json()

        # 진행 중인 미션 찾기
        mission = next(
            (m for m in data["data"] if m["id"] == str(taxi_mission_template.id)),
            None,
        )
        assert mission is not None
        assert mission["user_progress"] is not None
        assert mission["user_progress"]["status"] == "in_progress"

    def test_list_missions_empty(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """미션이 없을 때 빈 목록"""
        response = auth_client.get("/missions")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
