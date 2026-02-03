"""DELETE /translation/threads/{thread_id} 엔드포인트

번역 스레드 삭제 API (soft delete)
Controller는 HTTP 처리만 담당, 비즈니스 로직은 Use Case에서 처리
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from ._use_cases import DeleteThreadUseCase

router = APIRouter(tags=["translation-threads"])


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.delete(
    "/translation/threads/{thread_id}",
    response_model=ApiResponse[None],
)
def delete_thread(
    thread_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[None]:
    """번역 스레드 삭제 (soft delete)

    Raises:
        ThreadNotFoundError: 스레드를 찾을 수 없음 (404)
    """
    # Use Case 실행 (존재 확인, 소유권 확인, soft delete)
    use_case = DeleteThreadUseCase(session)
    use_case.execute(thread_id=thread_id, profile_id=profile.id)

    return ApiResponse(
        status=Status.SUCCESS,
        message="스레드를 삭제했어요",
        data=None,
    )
