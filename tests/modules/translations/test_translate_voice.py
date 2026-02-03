"""POST /translate/voice 테스트

SPEC 기반 테스트 케이스:
- TC-T-003: 음성 번역
- TC-T-103: 잘못된 오디오
"""

from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.modules.profiles import Profile


class TestTranslateVoice:
    """POST /translate/voice 테스트"""

    def test_translate_voice_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-T-003: 음성 번역 성공"""
        # 가짜 오디오 파일 생성
        audio_content = b"fake audio content"

        with (
            patch(
                "src.modules.translations._translation_service.speech_to_text"
            ) as mock_stt,
            patch(
                "src.modules.translations._translation_service.translate"
            ) as mock_translate,
            patch(
                "src.modules.translations._translation_service.text_to_speech"
            ) as mock_tts,
        ):
            mock_stt.return_value = {"text": "안녕하세요", "confidence": 0.95}
            mock_translate.return_value = "Hello"
            mock_tts.return_value = {
                "audio_url": "https://storage.supabase.co/tts/abc123.mp3",
                "duration_ms": 1500,
            }

            response = auth_client.post(
                "/translate/voice",
                data={
                    "source_lang": "ko",
                    "target_lang": "en",
                },
                files={"audio_file": ("audio.wav", BytesIO(audio_content), "audio/wav")},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "음성 번역이 완료됐어요"
        assert data["data"]["translation_type"] == "voice"
        assert "audio_url" in data["data"]
        assert "confidence_score" in data["data"]

    def test_translate_voice_invalid_audio(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-T-103: 잘못된 오디오 파일 -> 400"""
        with patch(
            "src.modules.translations._translation_service.speech_to_text"
        ) as mock_stt:
            # ValueError는 오디오 검증 실패를 나타냄
            mock_stt.side_effect = ValueError("Invalid audio format")

            response = auth_client.post(
                "/translate/voice",
                data={
                    "source_lang": "ko",
                    "target_lang": "en",
                },
                files={
                    "audio_file": ("audio.txt", BytesIO(b"not audio"), "text/plain")
                },
            )

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "ERROR_INVALID_AUDIO"
