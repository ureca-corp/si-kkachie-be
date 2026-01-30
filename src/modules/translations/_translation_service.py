"""translations 외부 API 서비스 (공유)

Google Cloud Translation, Speech-to-Text, Text-to-Speech API 호출
"""


def translate(text: str, source_lang: str, target_lang: str) -> str:
    """Google Cloud Translation API로 텍스트 번역

    Args:
        text: 번역할 텍스트
        source_lang: 원본 언어 코드 (예: "en", "ko", "en-US")
        target_lang: 대상 언어 코드 (예: "en", "ko", "ko-KR")

    Returns:
        번역된 텍스트
    """
    # TODO: 실제 구현
    # from src.external.translation import get_translation_provider
    # provider = get_translation_provider()
    # return provider.translate(text, source_lang, target_lang)

    # 언어 코드 정규화 (en-US -> en, ko-KR -> ko, EN -> en)
    src = source_lang.split("-")[0].lower() if source_lang else ""
    tgt = target_lang.split("-")[0].lower() if target_lang else ""

    # 임시 구현 (테스트용)
    if src == "ko" and tgt == "en":
        return "Hello"
    elif src == "en" and tgt == "ko":
        return "안녕하세요"
    return text


def speech_to_text(audio_data: bytes, language: str) -> dict:
    """Google Cloud Speech-to-Text API

    Args:
        audio_data: 오디오 바이너리 데이터
        language: 음성 언어 코드 (예: "en", "ko")

    Returns:
        dict: {"text": 인식된 텍스트, "confidence": 신뢰도}
    """
    # TODO: 실제 Google Cloud Speech-to-Text 구현
    # from src.external.speech import get_speech_provider
    # provider = get_speech_provider()
    # if provider:
    #     return provider.speech_to_text(audio_data, language)

    # 임시 구현 (테스트용) - language에 따라 다른 mock 응답
    # 언어 코드 정규화 (en-US -> en, ko-KR -> ko)
    lang_code = language.split("-")[0].lower() if language else "ko"

    if lang_code == "en":
        return {"text": "Hello", "confidence": 0.95}
    elif lang_code == "ko":
        return {"text": "안녕하세요", "confidence": 0.95}
    else:
        # 지원하지 않는 언어는 원본 그대로 반환 (기본값)
        return {"text": "Hello", "confidence": 0.90}


def text_to_speech(text: str, language: str) -> dict:
    """Google Cloud Text-to-Speech API"""
    # TODO: 실제 구현
    return {
        "audio_url": "https://storage.supabase.co/tts/abc123.mp3",
        "duration_ms": 1500,
    }
