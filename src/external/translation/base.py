"""Translation Provider 인터페이스 및 에러 클래스 (Strategy Pattern)"""

from abc import ABC, abstractmethod


class TranslationError(Exception):
    """Translation API 에러"""

    def __init__(self, message: str, code: int | None = None):
        self.message = message
        self.code = code
        super().__init__(message)


class ITranslationProvider(ABC):
    """번역 공급자 인터페이스 (동기)"""

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """텍스트 번역

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드 (예: "en", "ko")
            target_lang: 대상 언어 코드 (예: "en", "ko")

        Returns:
            번역된 텍스트
        """
        ...

    def translate_with_context(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """컨텍스트 기반 번역 (기본 구현: 일반 번역으로 fallback)

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드
            target_lang: 대상 언어 코드
            context: 번역 컨텍스트 (상황 설명)

        Returns:
            번역된 텍스트
        """
        # 기본 구현: 컨텍스트 무시하고 일반 번역
        return self.translate(text, source_lang, target_lang)


class IAsyncTranslationProvider(ABC):
    """번역 공급자 인터페이스 (비동기)"""

    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """텍스트 번역

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드 (예: "en", "ko")
            target_lang: 대상 언어 코드 (예: "en", "ko")

        Returns:
            번역된 텍스트
        """
        ...

    async def translate_with_context(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """컨텍스트 기반 번역 (기본 구현: 일반 번역으로 fallback)

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드
            target_lang: 대상 언어 코드
            context: 번역 컨텍스트 (상황 설명)

        Returns:
            번역된 텍스트
        """
        # 기본 구현: 컨텍스트 무시하고 일반 번역
        return await self.translate(text, source_lang, target_lang)
