"""Translation Provider 인터페이스 (Strategy Pattern)"""

from abc import ABC, abstractmethod


class ITranslationProvider(ABC):
    """번역 공급자 인터페이스"""

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
