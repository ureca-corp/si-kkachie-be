"""컨텍스트 프롬프트 서비스 구현

카테고리별 AI 번역 컨텍스트 프롬프트를 조회하고 적용하는 서비스
사용자의 현재 상황 정보(1차, 2차 카테고리)를 포함한 전체 프롬프트 생성
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._interfaces import IContextService

if TYPE_CHECKING:
    from ._interfaces import ICategoryRepository


class ContextService(IContextService):
    """컨텍스트 서비스 구현"""

    def __init__(self, category_repository: ICategoryRepository) -> None:
        """컨텍스트 서비스 초기화

        Args:
            category_repository: 카테고리 Repository (DIP)
        """
        self._category_repository = category_repository

    def build_translation_context(
        self,
        primary_code: str | None,
        sub_code: str | None,
        target_lang: str = "ko",
    ) -> str | None:
        """번역용 전체 컨텍스트 빌드

        사용자의 현재 상황 정보와 카테고리별 프롬프트를 결합하여
        AI 번역에 사용할 전체 컨텍스트를 생성합니다.

        예시 출력:
        "이 사용자는 음식점에서 주문하기를 원합니다.
         음식점 주문 상황입니다. 메뉴, 수량, 요청사항 관련 표현을 자연스럽게 번역해주세요."

        Args:
            primary_code: 1차 카테고리 코드 (선택)
            sub_code: 2차 카테고리 코드 (선택)
            target_lang: 타겟 언어

        Returns:
            번역에 사용할 컨텍스트 문자열 또는 None
        """
        if not primary_code or not sub_code:
            return None

        # 카테고리 이름 조회
        primary_name, sub_name = self._get_category_names(
            primary_code, sub_code, target_lang
        )

        # 사용자 상황 설명 생성
        if target_lang == "ko":
            situation = f"이 사용자는 {primary_name}에서 {sub_name}을(를) 원합니다."
        else:
            situation = f"This user wants {sub_name} at a {primary_name}."

        # DB에서 카테고리별 프롬프트 조회
        category_prompt = self._get_context_prompt(primary_code, sub_code, target_lang)

        # 전체 컨텍스트 조합
        if category_prompt:
            return f"{situation}\n{category_prompt}"
        return situation

    def _get_context_prompt(
        self,
        primary_code: str,
        sub_code: str,
        target_lang: str = "ko",
    ) -> str | None:
        """카테고리별 컨텍스트 프롬프트 조회"""
        prompt = self._category_repository.get_context_prompt(primary_code, sub_code)
        if prompt is None:
            return None

        # 타겟 언어에 따라 프롬프트 선택
        if target_lang == "ko":
            return prompt.prompt_ko
        return prompt.prompt_en

    def _get_category_names(
        self,
        primary_code: str,
        sub_code: str,
        lang: str = "ko",
    ) -> tuple[str, str]:
        """카테고리 코드를 이름으로 변환"""
        # 1차 카테고리 조회
        primaries = self._category_repository.get_primary_categories()
        primary_name = primary_code
        for p in primaries:
            if p.code == primary_code:
                primary_name = p.name_ko if lang == "ko" else p.name_en
                break

        # 2차 카테고리 조회
        subs = self._category_repository.get_sub_categories()
        sub_name = sub_code
        for s in subs:
            if s.code == sub_code:
                sub_name = s.name_ko if lang == "ko" else s.name_en
                break

        return primary_name, sub_name
