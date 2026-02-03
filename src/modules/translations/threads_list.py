"""GET /translation/threads 엔드포인트

번역 스레드 목록 조회 API
Controller는 HTTP 처리만 담당, 비즈니스 로직은 Use Case에서 처리
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from ._use_cases import ListThreadsUseCase

router = APIRouter(tags=["translation-threads"])


# ─────────────────────────────────────────────────
# Response DTOs
# ─────────────────────────────────────────────────


class ThreadListItem(BaseModel):
    """스레드 목록 아이템"""

    id: str
    primary_category: str
    sub_category: str
    created_at: datetime


class PaginationInfo(BaseModel):
    """페이지네이션 정보"""

    page: int
    limit: int
    total: int
    total_pages: int


class ThreadListData(BaseModel):
    """스레드 목록 응답 데이터"""

    items: list[ThreadListItem]
    pagination: PaginationInfo


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.get("/translation/threads", response_model=ApiResponse[ThreadListData])
def list_threads(
    profile: CurrentProfile,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> ApiResponse[ThreadListData]:
    """번역 스레드 목록 조회"""
    # Use Case 실행
    use_case = ListThreadsUseCase(session)
    result = use_case.execute(profile_id=profile.id, page=page, limit=limit)

    # 응답 변환
    items = [
        ThreadListItem(
            id=str(t.id),
            primary_category=t.primary_category,
            sub_category=t.sub_category,
            created_at=t.created_at,
        )
        for t in result.items
    ]

    total_pages = (
        (result.total + result.limit - 1) // result.limit if result.total > 0 else 0
    )

    return ApiResponse(
        status=Status.SUCCESS,
        message="스레드 목록을 조회했어요",
        data=ThreadListData(
            items=items,
            pagination=PaginationInfo(
                page=result.page,
                limit=result.limit,
                total=result.total,
                total_pages=total_pages,
            ),
        ),
    )
