"""POST /translation/threads 엔드포인트

번역 스레드 생성 API
Controller는 HTTP 처리만 담당, 비즈니스 로직은 Use Case에서 처리
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from ._use_cases import CreateThreadUseCase

router = APIRouter(tags=["translation-threads"])


# ─────────────────────────────────────────────────
# Request/Response DTOs
# ─────────────────────────────────────────────────


class CreateThreadRequest(BaseModel):
    """스레드 생성 요청"""

    primary_category: str
    sub_category: str


class ThreadResponse(BaseModel):
    """스레드 응답"""

    id: str
    primary_category: str
    sub_category: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.post(
    "/translation/threads",
    response_model=ApiResponse[ThreadResponse],
    status_code=201,
)
def create_thread(
    body: CreateThreadRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[ThreadResponse]:
    """번역 스레드 생성

    Raises:
        InvalidCategoryError: 유효하지 않은 카테고리 조합 (400)
    """
    # Repository 인스턴스 생성 (DIP)
    from ._repository import CategoryRepository, ThreadRepository

    category_repository = CategoryRepository(session)
    thread_repository = ThreadRepository(session)

    # Use Case 실행
    use_case = CreateThreadUseCase(
        session=session,
        category_repository=category_repository,
        thread_repository=thread_repository,
    )
    result = use_case.execute(
        profile_id=profile.id,
        primary_category=body.primary_category,
        sub_category=body.sub_category,
    )

    # 응답 변환
    return ApiResponse(
        status=Status.SUCCESS,
        message="번역 스레드를 생성했어요",
        data=ThreadResponse(
            id=str(result.id),
            primary_category=result.primary_category,
            sub_category=result.sub_category,
            created_at=result.created_at,
        ),
    )
