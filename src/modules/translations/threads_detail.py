"""GET /translation/threads/{thread_id} 엔드포인트

번역 스레드 상세 조회 API (번역 기록 포함)
Controller는 HTTP 처리만 담당, 비즈니스 로직은 Use Case에서 처리
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from ._use_cases import GetThreadUseCase

router = APIRouter(tags=["translation-threads"])


# ─────────────────────────────────────────────────
# Response DTOs
# ─────────────────────────────────────────────────


class TranslationInThread(BaseModel):
    """스레드 내 번역 기록"""

    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    translation_type: str
    audio_url: str | None = None
    created_at: datetime


class ThreadDetailData(BaseModel):
    """스레드 상세 응답 데이터"""

    id: str
    primary_category: str
    sub_category: str
    created_at: datetime
    translations: list[TranslationInThread]


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.get(
    "/translation/threads/{thread_id}",
    response_model=ApiResponse[ThreadDetailData],
)
def get_thread(
    thread_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[ThreadDetailData]:
    """번역 스레드 상세 조회

    Raises:
        ThreadNotFoundError: 스레드를 찾을 수 없음 (404)
    """
    # Use Case 실행
    use_case = GetThreadUseCase(session)
    result = use_case.execute(thread_id=thread_id, profile_id=profile.id)

    # 응답 변환
    translation_items = [
        TranslationInThread(
            id=str(t.id),
            source_text=t.source_text,
            translated_text=t.translated_text,
            source_lang=t.source_lang,
            target_lang=t.target_lang,
            translation_type=t.translation_type,
            audio_url=t.audio_url,
            created_at=t.created_at,
        )
        for t in result.translations
    ]

    return ApiResponse(
        status=Status.SUCCESS,
        message="스레드를 조회했어요",
        data=ThreadDetailData(
            id=str(result.id),
            primary_category=result.primary_category,
            sub_category=result.sub_category,
            created_at=result.created_at,
            translations=translation_items,
        ),
    )
