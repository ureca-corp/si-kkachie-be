"""DELETE /users/me

회원 탈퇴
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import get_current_profile
from src.core.response import ApiResponse, Status

from . import _repository as repository
from ._models import Profile

router = APIRouter(tags=["users"])


@router.delete("/users/me", response_model=ApiResponse)
def delete_me(
    profile: Annotated[Profile, Depends(get_current_profile)],
    session: Session = Depends(get_session),
) -> ApiResponse:
    """회원 탈퇴"""
    repository.delete(session, profile)

    return ApiResponse(
        status=Status.SUCCESS,
        message="회원 탈퇴가 완료됐어요",
    )
