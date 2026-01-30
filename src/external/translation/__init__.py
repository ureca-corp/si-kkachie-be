"""Translation Provider 모듈

Google Cloud Translation API 연동
"""

from src.core.config import settings

from .base import ITranslationProvider

_translation_instance: ITranslationProvider | None = None


def get_translation_provider() -> ITranslationProvider | None:
    """Translation 공급자 반환 (설정 없으면 None)

    Note:
        GOOGLE_APPLICATION_CREDENTIALS 환경변수 설정 필요
    """
    global _translation_instance

    if not settings.GOOGLE_CLOUD_PROJECT:
        return None

    if _translation_instance is not None:
        return _translation_instance

    from .google_provider import GoogleTranslationProvider

    _translation_instance = GoogleTranslationProvider(
        project_id=settings.GOOGLE_CLOUD_PROJECT,
    )
    return _translation_instance


__all__ = [
    "ITranslationProvider",
    "get_translation_provider",
]
