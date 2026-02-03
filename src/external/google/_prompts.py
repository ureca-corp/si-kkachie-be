"""Vertex AI 프롬프트 템플릿"""

# 언어 코드 -> 언어 이름 매핑
LANG_NAMES = {
    "ko": "한국어",
    "en": "영어",
    "ja": "일본어",
    "zh": "중국어",
}


def get_language_name(lang_code: str) -> str:
    """언어 코드를 언어 이름으로 변환"""
    lang_code = lang_code.split("-")[0].lower() if lang_code else "ko"
    return LANG_NAMES.get(lang_code, lang_code)


def build_translation_prompt(
    text: str,
    target_lang_name: str,
    context: str | None = None,
) -> str:
    """번역 프롬프트 생성"""
    if context:
        return f"""당신은 전문 번역가입니다.

{context}

위 상황을 고려하여 다음 텍스트를 {target_lang_name}로 자연스럽게 번역해주세요.
번역 결과만 출력하고, 다른 설명은 하지 마세요.

원문: {text}

번역:"""
    return f"""당신은 전문 번역가입니다.
다음 텍스트를 {target_lang_name}로 자연스럽게 번역해주세요.
번역 결과만 출력하고, 다른 설명은 하지 마세요.

원문: {text}

번역:"""
