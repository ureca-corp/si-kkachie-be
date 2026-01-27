"""translations 도메인 Request/Response DTO"""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class TextTranslateRequest(BaseModel):
    """텍스트 번역 요청"""

    source_text: str = Field(min_length=1, max_length=5000)
    source_lang: str = Field(pattern=r"^(ko|en)$")
    target_lang: str = Field(pattern=r"^(ko|en)$")
    mission_progress_id: str | None = None

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


class TranslationListResponse(BaseModel):
    """번역 목록 응답"""

    items: list[TranslationResponse]
    pagination: dict


class PaginationInfo(BaseModel):
    """페이지네이션 정보"""

    page: int
    limit: int
    total: int
    total_pages: int
