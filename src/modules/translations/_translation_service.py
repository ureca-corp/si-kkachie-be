"""translations 번역 서비스 구현

Vertex AI (Gemini) 번역 API 호출
Provider가 설정되지 않으면 mock 응답 반환 (개발/테스트용)
"""

from src.external.translation import ITranslationProvider, get_translation_provider

from ._interfaces import ITranslationService


class TranslationService(ITranslationService):
    """Vertex AI 기반 번역 서비스 구현"""

    def __init__(self, provider: ITranslationProvider | None = None) -> None:
        """번역 서비스 초기화

        Args:
            provider: 번역 Provider (None이면 자동 생성)
        """
        self._provider = provider if provider is not None else get_translation_provider()

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """텍스트 번역 (Vertex AI Gemini)

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드 (예: "en", "ko", "en-US")
            target_lang: 대상 언어 코드 (예: "en", "ko", "ko-KR")
            context: 번역 컨텍스트 (상황 설명, 선택)

        Returns:
            번역된 텍스트
        """
        if self._provider:
            return self._provider.translate_with_context(
                text, source_lang, target_lang, context
            )

        # Fallback: Mock 응답 (개발/테스트용)
        return self._mock_translate(source_lang, target_lang, text)

    def _mock_translate(self, source_lang: str, target_lang: str, text: str) -> str:
        """Mock 번역 (Provider 없을 때)"""
        src = source_lang.split("-")[0].lower() if source_lang else ""
        tgt = target_lang.split("-")[0].lower() if target_lang else ""

        if src == "ko" and tgt == "en":
            return "Hello"
        elif src == "en" and tgt == "ko":
            return "안녕하세요"
        return text


# Factory 함수 (하위 호환성 및 편의용)
def get_translation_service() -> ITranslationService:
    """번역 서비스 인스턴스 반환"""
    return TranslationService()
