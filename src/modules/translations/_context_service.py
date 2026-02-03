"""컨텍스트 프롬프트 서비스

카테고리별 AI 번역 컨텍스트 프롬프트를 조회하고 적용하는 서비스
사용자의 현재 상황 정보(1차, 2차 카테고리)를 포함한 전체 프롬프트 생성
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


def _get_category_names(
    session: Session,
    primary_code: str,
    sub_code: str,
    lang: str = "ko",
) -> tuple[str, str]:
    """카테고리 코드를 이름으로 변환

    Args:
        session: DB 세션
        primary_code: 1차 카테고리 코드
        sub_code: 2차 카테고리 코드
        lang: 언어 (ko, en)

    Returns:
        (1차 카테고리 이름, 2차 카테고리 이름)
    """
    # 1차 카테고리 조회
    primaries = _repository.get_primary_categories(session)
    primary_name = primary_code
    for p in primaries:
        if p.code == primary_code:
            primary_name = p.name_ko if lang == "ko" else p.name_en
            break

    # 2차 카테고리 조회
    subs = _repository.get_sub_categories(session)
    sub_name = sub_code
    for s in subs:
        if s.code == sub_code:
            sub_name = s.name_ko if lang == "ko" else s.name_en
            break

    return primary_name, sub_name


def build_translation_context(
    session: Session,
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
        session: DB 세션
        primary_code: 1차 카테고리 코드 (선택)
        sub_code: 2차 카테고리 코드 (선택)
        target_lang: 타겟 언어

    Returns:
        번역에 사용할 컨텍스트 문자열 또는 None
    """
    if not primary_code or not sub_code:
        return None

    # 카테고리 이름 조회
    primary_name, sub_name = _get_category_names(
        session, primary_code, sub_code, target_lang
    )

    # 사용자 상황 설명 생성
    if target_lang == "ko":
        situation = f"이 사용자는 {primary_name}에서 {sub_name}을(를) 원합니다."
    else:
        situation = f"This user wants {sub_name} at a {primary_name}."

    # DB에서 카테고리별 프롬프트 조회
    category_prompt = get_context_prompt(session, primary_code, sub_code, target_lang)

    # 전체 컨텍스트 조합
    if category_prompt:
        return f"{situation}\n{category_prompt}"
    return situation
