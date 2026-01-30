"""Speech Provider 모듈

Google Cloud Speech-to-Text, Text-to-Speech API 연동
"""

from src.core.config import settings

from .base import ISpeechProvider

_speech_instance: ISpeechProvider | None = None


def get_speech_provider() -> ISpeechProvider | None:
    """Speech 공급자 반환 (설정 없으면 None)

    Note:
        GOOGLE_APPLICATION_CREDENTIALS 환경변수 설정 필요
    """
    global _speech_instance

    if not settings.GOOGLE_CLOUD_PROJECT:
        return None

    if _speech_instance is not None:
        return _speech_instance

    from .google_provider import GoogleSpeechProvider

    _speech_instance = GoogleSpeechProvider()
    return _speech_instance


__all__ = [
    "ISpeechProvider",
    "get_speech_provider",
]
