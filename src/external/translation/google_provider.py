"""Google Cloud Translation Provider

Google Cloud Translation API v3 구현
"""

import json

from google.cloud import translate_v3 as translate
from google.oauth2 import service_account

from src.core.config import settings

from .base import ITranslationProvider


def _get_credentials() -> service_account.Credentials | None:
    """Google Cloud 인증 정보 가져오기

    GOOGLE_CREDENTIALS_JSON 환경변수가 있으면 JSON 파싱,
    없으면 GOOGLE_APPLICATION_CREDENTIALS 파일 경로 사용 (기본 동작)
    """
    if settings.GOOGLE_CREDENTIALS_JSON:
        info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
        return service_account.Credentials.from_service_account_info(info)
    return None  # 기본 ADC 사용


class GoogleTranslationProvider(ITranslationProvider):
    """Google Cloud Translation 공급자"""

    def __init__(self, project_id: str) -> None:
        """Google Cloud Translation 클라이언트 초기화

        Args:
            project_id: Google Cloud 프로젝트 ID
        """
        credentials = _get_credentials()
        self._client = translate.TranslationServiceClient(credentials=credentials)
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
