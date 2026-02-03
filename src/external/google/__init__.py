"""Google Vertex AI Provider

Vertex AI (Gemini) 기반 AI 기능 연동

기능 목록:
1. 범용 콘텐츠 생성 - generate_content()
2. 컨텍스트 기반 번역 - translate()
"""

import os

from src.core.config import settings

from ._base import IAsyncVertexAIProvider, IVertexAIProvider, VertexAIError

_vertex_instance: IVertexAIProvider | None = None
_async_vertex_instance: IAsyncVertexAIProvider | None = None


def _has_google_credentials() -> bool:
    """Google Cloud 인증 정보 존재 여부"""
    return bool(
        settings.GOOGLE_CREDENTIALS_JSON
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )


def get_vertex_provider() -> IVertexAIProvider | None:
    """Vertex AI Provider 반환 - 동기

    Note:
        GOOGLE_CLOUD_PROJECT와 GOOGLE_CREDENTIALS_JSON (또는 ADC) 필요
    """
    global _vertex_instance

    if not settings.GOOGLE_CLOUD_PROJECT or not _has_google_credentials():
        return None

    if _vertex_instance is not None:
        return _vertex_instance

    from .gemini import VertexAIProvider

    _vertex_instance = VertexAIProvider(
        project_id=settings.GOOGLE_CLOUD_PROJECT,
    )
    return _vertex_instance


def get_async_vertex_provider() -> IAsyncVertexAIProvider | None:
    """Vertex AI Provider 반환 - 비동기

    Note:
        GOOGLE_CLOUD_PROJECT와 GOOGLE_CREDENTIALS_JSON (또는 ADC) 필요
    """
    global _async_vertex_instance

    if not settings.GOOGLE_CLOUD_PROJECT or not _has_google_credentials():
        return None

    if _async_vertex_instance is not None:
        return _async_vertex_instance

    from .gemini import AsyncVertexAIProvider

    _async_vertex_instance = AsyncVertexAIProvider(
        project_id=settings.GOOGLE_CLOUD_PROJECT,
    )
    return _async_vertex_instance


__all__ = [
    "IAsyncVertexAIProvider",
    "IVertexAIProvider",
    "VertexAIError",
    "get_async_vertex_provider",
    "get_vertex_provider",
]
