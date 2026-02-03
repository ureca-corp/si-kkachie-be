"""Translation Provider 모듈

Google Cloud Translation API 및 Vertex AI (Gemini) 연동
"""

import os

from src.core.config import settings

from .base import ITranslationProvider

_translation_instance: ITranslationProvider | None = None
_vertex_instance: ITranslationProvider | None = None


def _has_google_credentials() -> bool:
    """Google Cloud 인증 정보 존재 여부"""
    return bool(
        settings.GOOGLE_CREDENTIALS_JSON
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )


def get_translation_provider() -> ITranslationProvider | None:
    """기본 Translation 공급자 반환 (Google Cloud Translation)

    Note:
        GOOGLE_CLOUD_PROJECT와 GOOGLE_CREDENTIALS_JSON (또는 ADC) 필요
    """
    global _translation_instance

    if not settings.GOOGLE_CLOUD_PROJECT or not _has_google_credentials():
        return None

    if _translation_instance is not None:
        return _translation_instance

    from .google_provider import GoogleTranslationProvider

    _translation_instance = GoogleTranslationProvider(
        project_id=settings.GOOGLE_CLOUD_PROJECT,
    )
    return _translation_instance


def get_vertex_provider() -> ITranslationProvider | None:
    """Vertex AI (Gemini) 공급자 반환 (컨텍스트 기반 번역용)

    Note:
        GOOGLE_CLOUD_PROJECT와 GOOGLE_CREDENTIALS_JSON (또는 ADC) 필요
    """
    global _vertex_instance

    if not settings.GOOGLE_CLOUD_PROJECT or not _has_google_credentials():
        return None

    if _vertex_instance is not None:
        return _vertex_instance

    from .vertex_provider import VertexTranslationProvider

    _vertex_instance = VertexTranslationProvider(
        project_id=settings.GOOGLE_CLOUD_PROJECT,
    )
    return _vertex_instance


__all__ = [
    "ITranslationProvider",
    "get_translation_provider",
    "get_vertex_provider",
]
