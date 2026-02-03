"""Translation Provider 모듈

Vertex AI (Gemini) 기반 번역 연동
동기/비동기 버전 모두 제공
"""

import os

from src.core.config import settings

from .base import (
    IAsyncTranslationProvider,
    ITranslationProvider,
    TranslationError,
)

_vertex_instance: ITranslationProvider | None = None
_async_vertex_instance: IAsyncTranslationProvider | None = None


def _has_google_credentials() -> bool:
    """Google Cloud 인증 정보 존재 여부"""
    return bool(
        settings.GOOGLE_CREDENTIALS_JSON
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )


def get_translation_provider() -> ITranslationProvider | None:
    """Vertex AI (Gemini) 번역 공급자 반환 - 동기

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


def get_async_translation_provider() -> IAsyncTranslationProvider | None:
    """Vertex AI (Gemini) 번역 공급자 반환 - 비동기

    Note:
        GOOGLE_CLOUD_PROJECT와 GOOGLE_CREDENTIALS_JSON (또는 ADC) 필요
    """
    global _async_vertex_instance

    if not settings.GOOGLE_CLOUD_PROJECT or not _has_google_credentials():
        return None

    if _async_vertex_instance is not None:
        return _async_vertex_instance

    from .vertex_provider import AsyncVertexTranslationProvider

    _async_vertex_instance = AsyncVertexTranslationProvider(
        project_id=settings.GOOGLE_CLOUD_PROJECT,
    )
    return _async_vertex_instance


__all__ = [
    # 인터페이스
    "ITranslationProvider",
    "IAsyncTranslationProvider",
    # 팩토리 함수
    "get_translation_provider",
    "get_async_translation_provider",
    # 에러 클래스
    "TranslationError",
]
