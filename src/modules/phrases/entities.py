"""phrases 도메인 Request/Response DTO"""

from pydantic import BaseModel


class PhraseResponse(BaseModel):
    """추천 문장 응답"""

    id: str
    text_ko: str
    text_en: str
    category: str
    usage_count: int

    model_config = {"from_attributes": True}


class PhraseUseResponse(BaseModel):
    """문장 사용 응답"""

    id: str
    usage_count: int
