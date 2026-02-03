"""Vertex AI (Gemini) Translation Provider

컨텍스트 기반 AI 번역을 위한 Vertex AI Gemini 구현
동기/비동기 버전 모두 제공
"""

import json

from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

from src.core.config import settings

from .base import IAsyncTranslationProvider, ITranslationProvider, TranslationError

# 언어 코드 → 언어 이름 매핑
_LANG_NAMES = {
    "ko": "한국어",
    "en": "영어",
    "ja": "일본어",
    "zh": "중국어",
}


def _get_credentials() -> service_account.Credentials | None:
    """Google Cloud 인증 정보 가져오기"""
    if settings.GOOGLE_CREDENTIALS_JSON:
        info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
        return service_account.Credentials.from_service_account_info(info)
    return None


def _get_language_name(lang_code: str) -> str:
    """언어 코드를 언어 이름으로 변환"""
    lang_code = lang_code.split("-")[0].lower() if lang_code else "ko"
    return _LANG_NAMES.get(lang_code, lang_code)


def _build_prompt(text: str, target_lang_name: str, context: str | None = None) -> str:
    """번역 프롬프트 생성"""
    if context:
        return f"""당신은 전문 번역가입니다.

{context}

위 상황을 고려하여 다음 텍스트를 {target_lang_name}로 자연스럽게 번역해주세요.
번역 결과만 출력하고, 다른 설명은 하지 마세요.

원문: {text}

번역:"""
    return f"""당신은 전문 번역가입니다.
다음 텍스트를 {target_lang_name}로 자연스럽게 번역해주세요.
번역 결과만 출력하고, 다른 설명은 하지 마세요.

원문: {text}

번역:"""


class VertexTranslationProvider(ITranslationProvider):
    """Vertex AI (Gemini) 기반 컨텍스트 번역 공급자 (동기)"""

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
        """기본 번역 (컨텍스트 없음)"""
        return self.translate_with_context(text, source_lang, target_lang, None)

    def translate_with_context(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """컨텍스트 기반 AI 번역 (동기)"""
        if not text:
            return ""

        try:
            target_lang_name = _get_language_name(target_lang)
            prompt = _build_prompt(text, target_lang_name, context)
            response = self._model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise TranslationError(f"Translation failed: {e}") from e


class AsyncVertexTranslationProvider(IAsyncTranslationProvider):
    """Vertex AI (Gemini) 기반 컨텍스트 번역 공급자 (비동기)"""

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

    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """기본 번역 (컨텍스트 없음)"""
        return await self.translate_with_context(text, source_lang, target_lang, None)

    async def translate_with_context(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """컨텍스트 기반 AI 번역 (비동기)"""
        if not text:
            return ""

        try:
            target_lang_name = _get_language_name(target_lang)
            prompt = _build_prompt(text, target_lang_name, context)
            response = await self._model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            raise TranslationError(f"Translation failed: {e}") from e
