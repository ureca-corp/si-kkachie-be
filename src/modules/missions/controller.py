"""missions 도메인 Controller

SPEC 기반 API:
- GET /missions (미션 목록 조회)
- GET /missions/{id} (미션 상세 조회)
- POST /missions/{id}/start (미션 시작)
- PATCH /missions/{id}/progress (단계 완료 처리)
- POST /missions/{id}/end (미션 종료)
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from . import service
from .entities import (
    EndMissionRequest,
    MissionDetailResponse,
    MissionEndResponse,
    MissionListItemResponse,
    MissionProgressUpdateResponse,
    MissionStartResponse,
    MissionStepResponse,
    UpdateProgressRequest,
    UserProgressResponse,
)

router = APIRouter(prefix="/missions", tags=["missions"])


@router.get(
    "",
    response_model=ApiResponse[list[MissionListItemResponse]],
    openapi_extra={
        "x-pages": ["home", "mission-list"],
        "x-agent-description": "미션 목록 조회. 홈 화면이나 미션 탭에서 사용 가능한 미션들을 보여줄 때 사용. 사용자의 진행 상태도 함께 반환",
    },
)
def list_missions(
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[list[MissionListItemResponse]]:
    """미션 목록 조회"""
    missions = service.get_missions_with_progress(
        session, profile.id, lang=profile.preferred_language
    )

    items = []
    for m in missions:
        user_progress = None
        if m["user_progress"]:
            user_progress = UserProgressResponse(**m["user_progress"])

        items.append(
            MissionListItemResponse(
                id=m["id"],
                title=m["title"],
                description=m["description"],
                mission_type=m["mission_type"],
                estimated_duration_min=m["estimated_duration_min"],
                icon_url=m["icon_url"],
                steps_count=m["steps_count"],
                user_progress=user_progress,
            )
        )

    return ApiResponse(
        status=Status.SUCCESS,
        message="조회에 성공했어요",
        data=items,
    )


@router.get(
    "/{mission_id}",
    response_model=ApiResponse[MissionDetailResponse],
    openapi_extra={
        "x-pages": ["mission-detail", "mission-play"],
        "x-agent-description": "미션 상세 정보 조회. 미션 상세 페이지에서 미션의 모든 단계, 추천 문장 등 세부 정보를 표시할 때 사용",
    },
)
def get_mission(
    mission_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[MissionDetailResponse] | JSONResponse:
    """미션 상세 조회"""
    from src.core.exceptions import NotFoundError

    try:
        mission = service.get_mission_detail(
            session, mission_id, profile.id, lang=profile.preferred_language
        )
    except NotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "status": Status.MISSION_NOT_FOUND,
                "message": "미션을 찾을 수 없어요",
                "data": None,
            },
        )

    user_progress = None
    if mission["user_progress"]:
        user_progress = UserProgressResponse(**mission["user_progress"])

    steps = [
        MissionStepResponse(
            id=s["id"],
            step_order=s["step_order"],
            title=s["title"],
            description=s["description"],
            is_completed=s["is_completed"],
            phrases=s["phrases"],
        )
        for s in mission["steps"]
    ]

    return ApiResponse(
        status=Status.SUCCESS,
        message="조회에 성공했어요",
        data=MissionDetailResponse(
            id=mission["id"],
            title=mission["title"],
            description=mission["description"],
            mission_type=mission["mission_type"],
            estimated_duration_min=mission["estimated_duration_min"],
            icon_url=mission["icon_url"],
            steps=steps,
            user_progress=user_progress,
        ),
    )


@router.post(
    "/{mission_id}/start",
    response_model=ApiResponse[MissionStartResponse],
    openapi_extra={
        "x-pages": ["mission-detail"],
        "x-agent-description": "미션 시작. 미션 상세 페이지에서 '시작하기' 버튼 클릭 시 호출. 이미 진행 중인 미션이면 409 에러 반환",
    },
)
def start_mission(
    mission_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[MissionStartResponse] | JSONResponse:
    """미션 시작"""
    from src.core.exceptions import ConflictError, NotFoundError

    try:
        progress = service.start_mission(session, mission_id, profile.id)

        return JSONResponse(
            status_code=201,
            content={
                "status": Status.SUCCESS,
                "message": "미션을 시작했어요",
                "data": {
                    "progress_id": str(progress.id),
                    "mission_id": str(progress.mission_template_id),
                    "status": progress.status,
                    "current_step": progress.current_step,
                    "started_at": (
                        progress.started_at.isoformat() if progress.started_at else None
                    ),
                },
            },
        )
    except NotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "status": Status.MISSION_NOT_FOUND,
                "message": "미션을 찾을 수 없어요",
                "data": None,
            },
        )
    except ConflictError:
        return JSONResponse(
            status_code=409,
            content={
                "status": Status.ERROR_MISSION_ALREADY_STARTED,
                "message": "이미 진행 중인 미션이에요",
                "data": None,
            },
        )


@router.patch(
    "/{mission_id}/progress",
    response_model=ApiResponse[MissionProgressUpdateResponse],
    openapi_extra={
        "x-pages": ["mission-play"],
        "x-agent-description": "미션 단계 완료 처리. 미션 진행 페이지에서 각 단계를 완료할 때 호출. 다음 단계로 진행하거나 미션 완료 상태 업데이트",
    },
)
def update_progress(
    mission_id: UUID,
    request: UpdateProgressRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[MissionProgressUpdateResponse] | JSONResponse:
    """단계 완료 처리"""
    from src.core.exceptions import ValidationError

    try:
        result = service.update_progress(session, mission_id, profile.id, request)

        return ApiResponse(
            status=Status.SUCCESS,
            message="단계를 완료했어요",
            data=MissionProgressUpdateResponse(**result),
        )
    except ValidationError:
        return JSONResponse(
            status_code=400,
            content={
                "status": Status.ERROR_MISSION_NOT_STARTED,
                "message": "시작된 미션이 없어요",
                "data": None,
            },
        )


@router.post(
    "/{mission_id}/end",
    response_model=ApiResponse[MissionEndResponse],
    openapi_extra={
        "x-pages": ["mission-play", "mission-complete"],
        "x-agent-description": "미션 종료. 미션 진행 페이지에서 미션을 완료하거나 포기할 때 호출. 성공/실패 상태와 함께 피드백 저장 가능",
    },
)
def end_mission(
    mission_id: UUID,
    request: EndMissionRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[MissionEndResponse] | JSONResponse:
    """미션 종료"""
    from src.core.exceptions import ValidationError

    try:
        result = service.end_mission(session, mission_id, profile.id, request)

        return ApiResponse(
            status=Status.SUCCESS,
            message="미션을 종료했어요",
            data=MissionEndResponse(**result),
        )
    except ValidationError:
        return JSONResponse(
            status_code=400,
            content={
                "status": Status.ERROR_MISSION_NOT_STARTED,
                "message": "시작된 미션이 없어요",
                "data": None,
            },
        )
