"""Translation Provider 모듈

Vertex AI (Gemini) 기반 번역 연동
"""

import os

from src.core.config import settings

from .base import ITranslationProvider

_vertex_instance: ITranslationProvider | None = None


def _has_google_credentials() -> bool:
    """Google Cloud 인증 정보 존재 여부"""
    return bool(
        settings.GOOGLE_CREDENTIALS_JSON
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )


def get_translation_provider() -> ITranslationProvider | None:
    """Vertex AI (Gemini) 번역 공급자 반환

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
]
