"""Vertex AI Gemini Provider

범용 콘텐츠 생성 및 번역

동기/비동기 버전 모두 제공
"""

import json

from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

from src.core.config import settings

from ._base import IAsyncVertexAIProvider, IVertexAIProvider, VertexAIError
from ._prompts import build_translation_prompt, get_language_name


def _get_credentials() -> service_account.Credentials | None:
    """Google Cloud 인증 정보 가져오기"""
    if settings.GOOGLE_CREDENTIALS_JSON:
        info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
        return service_account.Credentials.from_service_account_info(info)
    return None


class VertexAIProvider(IVertexAIProvider):
    """Vertex AI (Gemini) Provider (동기)"""

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

    def generate_content(self, prompt: str) -> str:
        """범용 콘텐츠 생성 (동기)"""
        if not prompt:
            return ""

        try:
            response = self._model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise VertexAIError(f"Content generation failed: {e}") from e

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """텍스트 번역 (동기)"""
        if not text:
            return ""

        try:
            target_lang_name = get_language_name(target_lang)
            prompt = build_translation_prompt(text, target_lang_name, context)
            response = self._model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise VertexAIError(f"Translation failed: {e}") from e


class AsyncVertexAIProvider(IAsyncVertexAIProvider):
    """Vertex AI (Gemini) Provider (비동기)"""

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

    async def generate_content(self, prompt: str) -> str:
        """범용 콘텐츠 생성 (비동기)"""
        if not prompt:
            return ""

        try:
            response = await self._model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            raise VertexAIError(f"Content generation failed: {e}") from e

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
    ) -> str:
        """텍스트 번역 (비동기)"""
        if not text:
            return ""

        try:
            target_lang_name = get_language_name(target_lang)
            prompt = build_translation_prompt(text, target_lang_name, context)
            response = await self._model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            raise VertexAIError(f"Translation failed: {e}") from e
