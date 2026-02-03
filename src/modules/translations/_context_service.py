"""컨텍스트 프롬프트 서비스

카테고리별 AI 번역 컨텍스트 프롬프트를 조회하고 적용하는 서비스
"""

from sqlmodel import Session

from . import _repository


def get_context_prompt(
    session: Session,
    primary_code: str,
    sub_code: str,
    target_lang: str = "ko",
) -> str | None:
    """카테고리별 컨텍스트 프롬프트 조회

    Args:
        session: DB 세션
        primary_code: 1차 카테고리 코드 (FD6, CE7 등)
        sub_code: 2차 카테고리 코드 (ordering, payment 등)
        target_lang: 타겟 언어 (ko, en)

    Returns:
        컨텍스트 프롬프트 문자열 또는 None
    """
    prompt = _repository.get_context_prompt(session, primary_code, sub_code)
    if prompt is None:
        return None

    # 타겟 언어에 따라 프롬프트 선택
    if target_lang == "ko":
        return prompt.prompt_ko
    return prompt.prompt_en


def build_translation_context(
    session: Session,
    primary_code: str | None,
    sub_code: str | None,
    target_lang: str = "ko",
) -> str | None:
    """번역용 전체 컨텍스트 빌드

    Args:
        session: DB 세션
        primary_code: 1차 카테고리 코드 (선택)
        sub_code: 2차 카테고리 코드 (선택)
        target_lang: 타겟 언어

    Returns:
        번역에 사용할 컨텍스트 문자열 또는 None
    """
    if not primary_code or not sub_code:
        return None

    return get_context_prompt(session, primary_code, sub_code, target_lang)
