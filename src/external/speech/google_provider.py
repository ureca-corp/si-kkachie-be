"""Google Cloud Speech Provider

Google Cloud Speech-to-Text 및 Text-to-Speech API 구현
"""

import json

from google.cloud import speech, texttospeech
from google.oauth2 import service_account

from src.core.config import settings

from .base import ISpeechProvider


def _get_credentials() -> service_account.Credentials | None:
    """Google Cloud 인증 정보 가져오기

    GOOGLE_CREDENTIALS_JSON 환경변수가 있으면 JSON 파싱,
    없으면 GOOGLE_APPLICATION_CREDENTIALS 파일 경로 사용 (기본 동작)
    """
    if settings.GOOGLE_CREDENTIALS_JSON:
        info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
        return service_account.Credentials.from_service_account_info(info)
    return None  # 기본 ADC 사용


class GoogleSpeechProvider(ISpeechProvider):
    """Google Cloud Speech 공급자"""

    # 언어 코드 매핑 (짧은 코드 -> BCP-47)
    LANGUAGE_MAP = {
        "en": "en-US",
        "ko": "ko-KR",
        "ja": "ja-JP",
        "zh": "zh-CN",
        "es": "es-ES",
        "fr": "fr-FR",
        "de": "de-DE",
    }

    def __init__(self) -> None:
        """Google Cloud 클라이언트 초기화"""
        credentials = _get_credentials()
        self._stt_client = speech.SpeechClient(credentials=credentials)
        self._tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

    def _normalize_language_code(self, language: str) -> str:
        """언어 코드를 BCP-47 형식으로 정규화

        Args:
            language: 언어 코드 (예: "en", "EN", "en-US", "ko-KR")

        Returns:
            BCP-47 형식 언어 코드 (예: "en-US", "ko-KR")
        """
        if not language:
            return "ko-KR"

        # 이미 BCP-47 형식이면 그대로 반환 (대소문자 정규화)
        if "-" in language:
            parts = language.split("-")
            return f"{parts[0].lower()}-{parts[1].upper()}"

        # 짧은 코드를 BCP-47로 변환
        short_code = language.lower()
        return self.LANGUAGE_MAP.get(short_code, f"{short_code}-{short_code.upper()}")

    def speech_to_text(self, audio_data: bytes, language: str) -> dict:
        """Google Cloud Speech-to-Text API 호출

        Args:
            audio_data: 오디오 바이너리 데이터 (WAV, MP3, FLAC 등)
            language: 음성 언어 코드

        Returns:
            dict: {"text": 인식된 텍스트, "confidence": 신뢰도}
        """
        language_code = self._normalize_language_code(language)

        # 오디오 설정 (자동 인코딩 및 샘플레이트 감지)
        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
            # sample_rate_hertz 생략 - WAV 헤더에서 자동 감지
            language_code=language_code,
            enable_automatic_punctuation=True,
        )

        # STT 요청
        response = self._stt_client.recognize(config=config, audio=audio)

        # 결과 파싱
        if not response.results:
            return {"text": "", "confidence": 0.0}

        result = response.results[0]
        if not result.alternatives:
            return {"text": "", "confidence": 0.0}

        alternative = result.alternatives[0]
        return {
            "text": alternative.transcript,
            "confidence": alternative.confidence,
        }

    def text_to_speech(self, text: str, language: str) -> dict:
        """Google Cloud Text-to-Speech API 호출

        Args:
            text: 변환할 텍스트
            language: 음성 언어 코드

        Returns:
            dict: {"audio_data": MP3 바이너리, "duration_ms": 예상 재생 시간}
        """
        language_code = self._normalize_language_code(language)

        # 텍스트 입력
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # 음성 설정
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )

        # 오디오 설정 (MP3)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
        )

        # TTS 요청
        response = self._tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        # 대략적인 재생 시간 추정 (텍스트 길이 기반)
        # 평균 발화 속도: 분당 150단어, 단어당 평균 5글자
        chars_per_ms = 150 * 5 / 60000  # 약 0.0125
        estimated_duration_ms = int(len(text) / chars_per_ms) if text else 0

        return {
            "audio_data": response.audio_content,
            "duration_ms": estimated_duration_ms,
        }
