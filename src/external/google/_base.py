"""Google Vertex AI 인터페이스 및 에러 클래스"""

from abc import ABC, abstractmethod


class VertexAIError(Exception):
    """Vertex AI API 에러"""

    def __init__(self, message: str, code: int | None = None):
        self.message = message
        self.code = code
        super().__init__(message)


class IVertexAIProvider(ABC):
    """Vertex AI Provider 인터페이스"""

    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        """범용 콘텐츠 생성 (동기)

        Args:
            prompt: 생성 프롬프트

        Returns:
            생성된 텍스트
        """
        ...

    @abstractmethod
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """텍스트 번역 (동기)

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드 (예: "en", "ko")
            target_lang: 대상 언어 코드 (예: "en", "ko")
            context: 번역 컨텍스트 (상황 설명, 선택)

        Returns:
            번역된 텍스트
        """
        ...


class IAsyncVertexAIProvider(ABC):
    """Vertex AI Provider 인터페이스 (비동기)"""

    @abstractmethod
    async def generate_content(self, prompt: str) -> str:
        """범용 콘텐츠 생성 (비동기)

        Args:
            prompt: 생성 프롬프트

        Returns:
            생성된 텍스트
        """
        ...

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """텍스트 번역 (비동기)

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드 (예: "en", "ko")
            target_lang: 대상 언어 코드 (예: "en", "ko")
            context: 번역 컨텍스트 (상황 설명, 선택)

        Returns:
            번역된 텍스트
        """
        ...
