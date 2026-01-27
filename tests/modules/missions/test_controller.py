"""missions 도메인 컨트롤러 테스트

SPEC 기반 테스트 케이스:
- TC-M-001: 미션 목록 조회
- TC-M-002: 미션 상세 조회
- TC-M-003: 미션 시작
- TC-M-004: 단계 완료
- TC-M-005: 미션 종료 (해결)
- TC-M-006: 미션 종료 (부분해결)
- TC-M-007: 미션 종료 (미해결)
- TC-M-101: 없는 미션 조회
- TC-M-102: 이미 시작한 미션
- TC-M-103: 시작 전 단계 완료
- TC-M-104: 잘못된 결과값
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.missions.models import (
    MissionProgress,
    MissionStep,
    MissionTemplate,
)
from src.modules.profiles.models import Profile


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
