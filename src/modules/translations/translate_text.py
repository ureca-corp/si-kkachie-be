"""POST /translate/text 엔드포인트

텍스트 번역 API
Controller는 HTTP 처리만 담당, 비즈니스 로직은 Use Case에서 처리
서비스 인스턴스를 생성하여 Use Case에 주입 (DIP)
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, model_validator
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from ._use_cases import CreateTextTranslationUseCase, TextTranslationInput

router = APIRouter(tags=["translations"])


# ─────────────────────────────────────────────────
# Request/Response DTOs
# ─────────────────────────────────────────────────


class TextTranslateRequest(BaseModel):
    """텍스트 번역 요청"""

    source_text: str = Field(min_length=1, max_length=5000)
    source_lang: str = Field(pattern=r"^(ko|en)$")
    target_lang: str = Field(pattern=r"^(ko|en)$")
    mission_progress_id: str | None = None
    thread_id: str | None = None
    context_primary: str | None = None  # 1차 카테고리 코드 (FD6, CE7 등)
    context_sub: str | None = None  # 2차 카테고리 코드 (ordering, payment 등)

    @model_validator(mode="after")
    def validate_different_languages(self):
        if self.source_lang == self.target_lang:
            msg = "같은 언어로는 번역할 수 없어요"
            raise ValueError(msg)
        return self


class TranslationResponse(BaseModel):
    """번역 응답"""

    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    translation_type: str
    mission_progress_id: str | None = None
    audio_url: str | None = None
    duration_ms: int | None = None
    confidence_score: float | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.post("/translate/text", response_model=ApiResponse[TranslationResponse])
def translate_text(
    request: TextTranslateRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[TranslationResponse]:
    """텍스트 번역"""
    # Use Case 입력 생성
    input_data = TextTranslationInput(
        profile_id=profile.id,
        source_text=request.source_text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        mission_progress_id=(
            UUID(request.mission_progress_id) if request.mission_progress_id else None
        ),
        thread_id=UUID(request.thread_id) if request.thread_id else None,
        context_primary=request.context_primary,
        context_sub=request.context_sub,
    )

    # Repository/Service 인스턴스 생성 (DIP)
    from ._context_service import ContextService
    from ._repository import CategoryRepository, TranslationRepository
    from ._translation_service import TranslationService

    translation_repository = TranslationRepository(session)
    category_repository = CategoryRepository(session)
    translation_service = TranslationService()
    context_service = ContextService(category_repository)

    # Use Case 실행
    use_case = CreateTextTranslationUseCase(
        session=session,
        translation_repository=translation_repository,
        translation_service=translation_service,
        context_service=context_service,
    )
    result = use_case.execute(input_data)

    # 응답 변환
    return ApiResponse(
        status=Status.SUCCESS,
        message="번역이 완료됐어요",
        data=TranslationResponse(
            id=str(result.id),
            source_text=result.source_text,
            translated_text=result.translated_text,
            source_lang=result.source_lang,
            target_lang=result.target_lang,
            translation_type=result.translation_type,
            mission_progress_id=(
                str(result.mission_progress_id) if result.mission_progress_id else None
            ),
            audio_url=result.audio_url,
            duration_ms=result.duration_ms,
            confidence_score=result.confidence_score,
            created_at=result.created_at,
        ),
    )
