"""GET /translation/categories 엔드포인트

번역 카테고리 목록 조회 API
- 1차 카테고리 (장소 유형)
- 2차 카테고리 (상황/의도)
- 카테고리 매핑 (유효한 조합)

Controller는 HTTP 처리만 담당, 비즈니스 로직은 Use Case에서 처리
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from ._use_cases import GetCategoriesUseCase

router = APIRouter(tags=["translation-categories"])


# ─────────────────────────────────────────────────
# Response DTOs
# ─────────────────────────────────────────────────


class PrimaryCategoryResponse(BaseModel):
    """1차 카테고리 응답"""

    code: str
    name_ko: str
    name_en: str


class SubCategoryResponse(BaseModel):
    """2차 카테고리 응답"""

    code: str
    name_ko: str
    name_en: str


class CategoriesData(BaseModel):
    """카테고리 목록 응답 데이터"""

    primary_categories: list[PrimaryCategoryResponse]
    sub_categories: list[SubCategoryResponse]
    mappings: dict[str, list[str]]  # primary_code -> [sub_codes]


# ─────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────


@router.get("/translation/categories", response_model=ApiResponse[CategoriesData])
def get_categories(
    _: CurrentProfile,  # 인증 필요
    session: Session = Depends(get_session),
) -> ApiResponse[CategoriesData]:
    """번역 카테고리 목록 조회"""
    # Use Case 실행
    use_case = GetCategoriesUseCase(session)
    result = use_case.execute()

    # 응답 변환
    primary_responses = [
        PrimaryCategoryResponse(
            code=p.code,
            name_ko=p.name_ko,
            name_en=p.name_en,
        )
        for p in result.primary_categories
    ]

    sub_responses = [
        SubCategoryResponse(
            code=s.code,
            name_ko=s.name_ko,
            name_en=s.name_en,
        )
        for s in result.sub_categories
    ]

    return ApiResponse(
        status=Status.SUCCESS,
        message="카테고리 목록을 조회했어요",
        data=CategoriesData(
            primary_categories=primary_responses,
            sub_categories=sub_responses,
            mappings=result.mappings,
        ),
    )
