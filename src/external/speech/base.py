"""Speech Provider 인터페이스 (Strategy Pattern)"""

from abc import ABC, abstractmethod


class ISpeechProvider(ABC):
    """음성 처리 공급자 인터페이스"""

    @abstractmethod
    def speech_to_text(self, audio_data: bytes, language: str) -> dict:
        """음성을 텍스트로 변환 (STT)

        Args:
            audio_data: 오디오 바이너리 데이터
            language: 음성 언어 코드 (예: "en", "ko", "en-US")

        Returns:
            dict: {"text": 인식된 텍스트, "confidence": 신뢰도 0.0~1.0}
        """
        ...

    @abstractmethod
    def text_to_speech(self, text: str, language: str) -> dict:
        """텍스트를 음성으로 변환 (TTS)

        Args:
            text: 변환할 텍스트
            language: 음성 언어 코드 (예: "en", "ko")

        Returns:
            dict: {"audio_data": 오디오 바이너리, "duration_ms": 재생 시간(ms)}
        """
        ...
