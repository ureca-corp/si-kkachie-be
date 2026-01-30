"""translations 외부 API 서비스 (공유)

Google Cloud Translation, Speech-to-Text, Text-to-Speech API 호출
Provider가 설정되지 않으면 mock 응답 반환 (개발/테스트용)
"""

from io import BytesIO
from uuid import uuid4

from src.external.speech import get_speech_provider
from src.external.storage import get_storage_provider
from src.external.translation import get_translation_provider


def translate(text: str, source_lang: str, target_lang: str) -> str:
    """텍스트 번역

    Args:
        text: 번역할 텍스트
        source_lang: 원본 언어 코드 (예: "en", "ko", "en-US")
        target_lang: 대상 언어 코드 (예: "en", "ko", "ko-KR")

    Returns:
        번역된 텍스트
    """
    provider = get_translation_provider()
    if provider:
        return provider.translate(text, source_lang, target_lang)

    # Fallback: Mock 응답 (개발/테스트용)
    src = source_lang.split("-")[0].lower() if source_lang else ""
    tgt = target_lang.split("-")[0].lower() if target_lang else ""

    if src == "ko" and tgt == "en":
        return "Hello"
    elif src == "en" and tgt == "ko":
        return "안녕하세요"
    return text


def speech_to_text(audio_data: bytes, language: str) -> dict:
    """음성을 텍스트로 변환 (STT)

    Args:
        audio_data: 오디오 바이너리 데이터
        language: 음성 언어 코드 (예: "en", "ko")

    Returns:
        dict: {"text": 인식된 텍스트, "confidence": 신뢰도}
    """
    provider = get_speech_provider()
    if provider:
        return provider.speech_to_text(audio_data, language)

    # Fallback: Mock 응답 (개발/테스트용)
    lang_code = language.split("-")[0].lower() if language else "ko"

    if lang_code == "en":
        return {"text": "Hello", "confidence": 0.95}
    elif lang_code == "ko":
        return {"text": "안녕하세요", "confidence": 0.95}
    else:
        return {"text": "Hello", "confidence": 0.90}


def text_to_speech(text: str, language: str) -> dict:
    """텍스트를 음성으로 변환 (TTS)

    Args:
        text: 변환할 텍스트
        language: 음성 언어 코드 (예: "en", "ko")

    Returns:
        dict: {"audio_url": 오디오 파일 URL, "duration_ms": 재생 시간(ms)}
    """
    speech_provider = get_speech_provider()
    storage_provider = get_storage_provider()

    if speech_provider and storage_provider:
        # 1. TTS로 오디오 생성
        tts_result = speech_provider.text_to_speech(text, language)
        audio_data = tts_result["audio_data"]
        duration_ms = tts_result["duration_ms"]

        # 2. Storage에 업로드
        file_key = f"tts/{uuid4()}.mp3"
        audio_url = storage_provider.upload(
            file=BytesIO(audio_data),
            key=file_key,
            content_type="audio/mpeg",
        )

        return {
            "audio_url": audio_url,
            "duration_ms": duration_ms,
        }

    # Fallback: Mock 응답 (개발/테스트용)
    return {
        "audio_url": "https://storage.example.com/tts/mock.mp3",
        "duration_ms": 1500,
    }
