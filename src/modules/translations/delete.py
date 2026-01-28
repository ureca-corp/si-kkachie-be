"""DELETE /translations/{id} 엔드포인트

번역 기록 삭제 기능을 담당하는 Vertical Slice
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.exceptions import NotFoundError
from src.core.response import ApiResponse, Status

from . import _repository

router = APIRouter(tags=["translations"])


# ─────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────


def delete_translation(
    session: Session,
    profile_id: UUID,
    translation_id: UUID,
) -> None:
    """번역 기록 삭제 (본인 것만)"""
    translation = _repository.get_by_id(session, translation_id)

    if not translation or translation.profile_id != profile_id:
        raise NotFoundError("번역 기록을 찾을 수 없어요")

    _repository.delete(session, translation)


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.delete("/translations/{translation_id}", response_model=ApiResponse)
def delete_translation_endpoint(
    translation_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse:
    """번역 기록 삭제"""
    delete_translation(session, profile.id, translation_id)

    return ApiResponse(
        status=Status.SUCCESS,
        message="번역 기록이 삭제됐어요",
    )
