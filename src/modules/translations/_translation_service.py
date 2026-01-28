"""translations 외부 API 서비스 (공유)

Google Cloud Translation, Speech-to-Text, Text-to-Speech API 호출
"""


def translate(text: str, source_lang: str, target_lang: str) -> str:
    """Google Cloud Translation API로 텍스트 번역"""
    # TODO: 실제 구현
    # from src.external.translation import get_translation_provider
    # provider = get_translation_provider()
    # return provider.translate(text, source_lang, target_lang)

    # 임시 구현 (테스트용)
    if source_lang == "ko" and target_lang == "en":
        return "Hello"
    elif source_lang == "en" and target_lang == "ko":
        return "안녕하세요"
    return text


def speech_to_text(audio_data: bytes, language: str) -> dict:
    """Google Cloud Speech-to-Text API"""
    # TODO: 실제 구현
    return {"text": "안녕하세요", "confidence": 0.95}


def text_to_speech(text: str, language: str) -> dict:
    """Google Cloud Text-to-Speech API"""
    # TODO: 실제 구현
    return {
        "audio_url": "https://storage.supabase.co/tts/abc123.mp3",
        "duration_ms": 1500,
    }
