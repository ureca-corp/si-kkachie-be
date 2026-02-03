"""Vertex AI (Gemini) Translation Provider

컨텍스트 기반 AI 번역을 위한 Vertex AI Gemini 구현
"""

import json

from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

from src.core.config import settings

from .base import ITranslationProvider


def _get_credentials() -> service_account.Credentials | None:
    """Google Cloud 인증 정보 가져오기"""
    if settings.GOOGLE_CREDENTIALS_JSON:
        info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
        return service_account.Credentials.from_service_account_info(info)
    return None


class VertexTranslationProvider(ITranslationProvider):
    """Vertex AI (Gemini) 기반 컨텍스트 번역 공급자"""

    def __init__(self, project_id: str, location: str = "us-central1") -> None:
        """Vertex AI 클라이언트 초기화

        Args:
            project_id: Google Cloud 프로젝트 ID
            location: Vertex AI 리전 (기본: us-central1, Gemini 모델 가용성 최적)
        """
        import vertexai

        credentials = _get_credentials()
        vertexai.init(
            project=project_id,
            location=location,
            credentials=credentials,
        )
        self._model = GenerativeModel("gemini-2.0-flash-lite-001")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """기본 번역 (컨텍스트 없음)

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드
            target_lang: 대상 언어 코드

        Returns:
            번역된 텍스트
        """
        return self.translate_with_context(text, source_lang, target_lang, None)

    def translate_with_context(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """컨텍스트 기반 AI 번역

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 코드 (예: "en", "ko")
            target_lang: 대상 언어 코드 (예: "en", "ko")
            context: 번역 컨텍스트 (상황 설명 + 프롬프트)

        Returns:
            번역된 텍스트
        """
        if not text:
            return ""

        target_lang_name = self._get_language_name(target_lang)

        # 프롬프트 구성
        if context:
            prompt = f"""당신은 전문 번역가입니다.

{context}

위 상황을 고려하여 다음 텍스트를 {target_lang_name}로 자연스럽게 번역해주세요.
번역 결과만 출력하고, 다른 설명은 하지 마세요.

원문: {text}

번역:"""
        else:
            prompt = f"""당신은 전문 번역가입니다.
다음 텍스트를 {target_lang_name}로 자연스럽게 번역해주세요.
번역 결과만 출력하고, 다른 설명은 하지 마세요.

원문: {text}

번역:"""

        response = self._model.generate_content(prompt)
        return response.text.strip()

    def _get_language_name(self, lang_code: str) -> str:
        """언어 코드를 언어 이름으로 변환"""
        lang_code = lang_code.split("-")[0].lower() if lang_code else "ko"
        lang_names = {
            "ko": "한국어",
            "en": "영어",
            "ja": "일본어",
            "zh": "중국어",
        }
        return lang_names.get(lang_code, lang_code)
