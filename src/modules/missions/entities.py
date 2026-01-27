"""missions 도메인 Request/Response DTO"""

from datetime import datetime

from pydantic import BaseModel, field_validator

from src.core.enums import MissionResult


class UpdateProgressRequest(BaseModel):
    """단계 완료 요청"""

    step_id: str
    is_completed: bool = True


class EndMissionRequest(BaseModel):
    """미션 종료 요청"""

    result: str

    @field_validator("result")
    @classmethod
    def validate_result(cls, v: str) -> str:
        valid_results = [r.value for r in MissionResult]
        if v not in valid_results:
            msg = "잘못된 결과 값이에요"
            raise ValueError(msg)
        return v


class MissionStepResponse(BaseModel):
    """미션 단계 응답"""

    id: str
    step_order: int
    title: str
    description: str
    is_completed: bool = False
    phrases: list[dict] = []


class UserProgressResponse(BaseModel):
    """사용자 진행 상태"""

    id: str | None = None
    status: str
    current_step: int
    started_at: datetime | None = None


class MissionListItemResponse(BaseModel):
    """미션 목록 아이템"""

    id: str
    title: str
    description: str
    mission_type: str
    estimated_duration_min: int
    icon_url: str | None = None
    steps_count: int
    user_progress: UserProgressResponse | None = None


class MissionDetailResponse(BaseModel):
    """미션 상세 응답"""

    id: str
    title: str
    description: str
    mission_type: str
    estimated_duration_min: int
    icon_url: str | None = None
    steps: list[MissionStepResponse]
    user_progress: UserProgressResponse | None = None


class MissionStartResponse(BaseModel):
    """미션 시작 응답"""

    progress_id: str
    mission_id: str
    status: str
    current_step: int
    started_at: datetime


class MissionProgressUpdateResponse(BaseModel):
    """단계 진행 응답"""

    progress_id: str
    current_step: int
    completed_steps: int
    total_steps: int


class MissionEndResponse(BaseModel):
    """미션 종료 응답"""

    progress_id: str
    status: str
    result: str
    ended_at: datetime
    duration_minutes: int
