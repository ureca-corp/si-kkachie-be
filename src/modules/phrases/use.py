"""POST /phrases/{id}/use - 문장 사용 기록

Vertical Slice: 하나의 엔드포인트에 필요한 모든 코드를 포함
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.exceptions import NotFoundError
from src.core.response import ApiResponse, Status

from . import _repository as repository

router = APIRouter()


# === Response DTO ===
class PhraseUseResponse(BaseModel):
    """문장 사용 응답"""

    id: str
    usage_count: int


# === Endpoint ===
@router.post("/{phrase_id}/use", response_model=ApiResponse[PhraseUseResponse])
def use_phrase(
    phrase_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[PhraseUseResponse] | JSONResponse:
    """문장 사용 기록

    - 문장의 usage_count를 1 증가시킵니다.
    - 비활성 문장은 사용할 수 없습니다.
    """
    try:
        phrase = repository.get_by_id(session, phrase_id)
        if not phrase or not phrase.is_active:
            raise NotFoundError("문장을 찾을 수 없어요")

        updated_phrase = repository.increment_usage_count(session, phrase)

        return ApiResponse(
            status=Status.SUCCESS,
            message="사용이 기록됐어요",
            data=PhraseUseResponse(
                id=str(updated_phrase.id),
                usage_count=updated_phrase.usage_count,
            ),
        )
    except NotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "status": Status.PHRASE_NOT_FOUND,
                "message": "문장을 찾을 수 없어요",
                "data": None,
            },
        )
