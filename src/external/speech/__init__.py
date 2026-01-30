"""Speech Provider 모듈

Google Cloud Speech-to-Text, Text-to-Speech API 연동
"""

from src.core.config import settings

from .base import ISpeechProvider

_speech_instance: ISpeechProvider | None = None


def get_speech_provider() -> ISpeechProvider | None:
    """Speech 공급자 반환 (설정 없으면 None)

    Note:
        GOOGLE_CLOUD_PROJECT와 GOOGLE_CREDENTIALS_JSON (또는 ADC) 필요
    """
    global _speech_instance

    # 프로젝트 ID 필수
    if not settings.GOOGLE_CLOUD_PROJECT:
        return None

    # 서버 환경: GOOGLE_CREDENTIALS_JSON 필수
    # 로컬 환경: GOOGLE_APPLICATION_CREDENTIALS 또는 gcloud ADC 사용
    import os

    has_credentials = bool(
        settings.GOOGLE_CREDENTIALS_JSON
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )
    if not has_credentials:
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
