"""Google Cloud Translation Provider

Google Cloud Translation API v3 구현
"""

from google.cloud import translate_v3 as translate

from .base import ITranslationProvider


class GoogleTranslationProvider(ITranslationProvider):
    """Google Cloud Translation 공급자"""

    def __init__(self, project_id: str) -> None:
        """Google Cloud Translation 클라이언트 초기화

        Args:
            project_id: Google Cloud 프로젝트 ID
        """
        self._client = translate.TranslationServiceClient()
        self._project_id = project_id
        self._parent = f"projects/{project_id}/locations/global"

    def _normalize_language_code(self, language: str) -> str:
        """언어 코드를 Google Translate 형식으로 정규화

        Args:
            language: 언어 코드 (예: "en", "EN", "en-US", "ko-KR")

        Returns:
            ISO 639-1 형식 언어 코드 (예: "en", "ko")
        """
        if not language:
            return "ko"

        # BCP-47 형식이면 앞부분만 추출
        if "-" in language:
            return language.split("-")[0].lower()

        return language.lower()

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Google Cloud Translation API 호출

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드
            target_lang: 대상 언어 코드

        Returns:
            번역된 텍스트
        """
        if not text:
            return ""

        source_code = self._normalize_language_code(source_lang)
        target_code = self._normalize_language_code(target_lang)

        # 같은 언어면 그대로 반환
        if source_code == target_code:
            return text

        response = self._client.translate_text(
            request={
                "parent": self._parent,
                "contents": [text],
                "source_language_code": source_code,
                "target_language_code": target_code,
                "mime_type": "text/plain",
            }
        )

        if not response.translations:
            return text

        return response.translations[0].translated_text
