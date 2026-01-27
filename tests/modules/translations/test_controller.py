"""translations 도메인 컨트롤러 테스트

SPEC 기반 테스트 케이스:
- TC-T-001: 텍스트 번역 (한->영)
- TC-T-002: 텍스트 번역 (영->한)
- TC-T-003: 음성 번역
- TC-T-004: 히스토리 조회
- TC-T-005: 기록 삭제
- TC-T-006: 대용량 텍스트 번역
- TC-T-101: 빈 텍스트
- TC-T-102: 같은 언어 번역
- TC-T-103: 잘못된 오디오
- TC-T-104: 타인 기록 삭제
- TC-T-105: 텍스트 길이 초과
"""

from io import BytesIO
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.profiles.models import Profile
from src.modules.translations.models import Translation


class TestTextTranslation:
    """POST /translate/text 테스트"""

    def test_translate_text_ko_to_en_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        text_translation_request: dict,
    ) -> None:
        """TC-T-001: 텍스트 번역 (한->영) 성공"""
        with patch(
            "src.modules.translations.service.translate_text"
        ) as mock_translate:
            mock_translate.return_value = "Hello"

            response = auth_client.post(
                "/translate/text",
                json=text_translation_request,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "번역이 완료됐어요"
        assert data["data"]["source_text"] == "안녕하세요"
        assert data["data"]["translated_text"] == "Hello"
        assert data["data"]["source_lang"] == "ko"
        assert data["data"]["target_lang"] == "en"
        assert data["data"]["translation_type"] == "text"

    def test_translate_text_en_to_ko_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-T-002: 텍스트 번역 (영->한) 성공"""
        with patch(
            "src.modules.translations.service.translate_text"
        ) as mock_translate:
            mock_translate.return_value = "안녕하세요"

            response = auth_client.post(
                "/translate/text",
                json={
                    "source_text": "Hello",
                    "source_lang": "en",
                    "target_lang": "ko",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["translated_text"] == "안녕하세요"

    def test_translate_text_empty_text(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-T-101: 빈 텍스트 -> 400"""
        response = auth_client.post(
            "/translate/text",
            json={
                "source_text": "",
                "source_lang": "ko",
                "target_lang": "en",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "VALIDATION_FAILED"

    def test_translate_text_same_language(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-T-102: 같은 언어 번역 -> 400"""
        response = auth_client.post(
            "/translate/text",
            json={
                "source_text": "안녕하세요",
                "source_lang": "ko",
                "target_lang": "ko",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "VALIDATION_FAILED"

    def test_translate_text_too_long(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-T-105: 텍스트 길이 초과 (5001자 이상) -> 400"""
        long_text = "가" * 5001  # 5001자

        response = auth_client.post(
            "/translate/text",
            json={
                "source_text": long_text,
                "source_lang": "ko",
                "target_lang": "en",
            },
        )

        assert response.status_code == 422

    def test_translate_text_max_length_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """TC-T-006: 대용량 텍스트 번역 (5000자) 성공"""
        max_text = "가" * 5000  # 정확히 5000자

        with patch(
            "src.modules.translations.service.translate_text"
        ) as mock_translate:
            mock_translate.return_value = "A" * 5000

            response = auth_client.post(
                "/translate/text",
                json={
                    "source_text": max_text,
                    "source_lang": "ko",
                    "target_lang": "en",
                },
            )

        assert response.status_code == 200


class TestVoiceTranslation:
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
                "src.modules.translations.service.speech_to_text"
            ) as mock_stt,
            patch(
                "src.modules.translations.service.translate_text"
            ) as mock_translate,
            patch(
                "src.modules.translations.service.text_to_speech"
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
            "src.modules.translations.service.speech_to_text"
        ) as mock_stt:
            mock_stt.side_effect = Exception("Invalid audio format")

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


class TestTranslationHistory:
    """GET /translations 테스트"""

    def test_get_translations_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_translation: Translation,
    ) -> None:
        """TC-T-004: 히스토리 조회 성공"""
        response = auth_client.get("/translations")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "조회에 성공했어요"
        assert "items" in data["data"]
        assert "pagination" in data["data"]
        assert len(data["data"]["items"]) >= 1

    def test_get_translations_with_pagination(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_translation: Translation,
    ) -> None:
        """페이지네이션 테스트"""
        response = auth_client.get("/translations?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 10

    def test_get_translations_filter_by_type(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_translation: Translation,
        voice_translation: Translation,
    ) -> None:
        """타입별 필터링 테스트"""
        response = auth_client.get("/translations?type=text")

        assert response.status_code == 200
        data = response.json()
        for item in data["data"]["items"]:
            assert item["translation_type"] == "text"

    def test_get_translations_empty(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """빈 목록 조회"""
        response = auth_client.get("/translations")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["items"] == []


class TestDeleteTranslation:
    """DELETE /translations/{id} 테스트"""

    def test_delete_translation_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        created_translation: Translation,
    ) -> None:
        """TC-T-005: 기록 삭제 성공"""
        response = auth_client.delete(f"/translations/{created_translation.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "번역 기록이 삭제됐어요"

    def test_delete_translation_not_found(
        self,
        auth_client: TestClient,
        test_profile: Profile,
    ) -> None:
        """존재하지 않는 기록 삭제 -> 404"""
        fake_id = uuid4()
        response = auth_client.delete(f"/translations/{fake_id}")

        assert response.status_code == 404

    def test_delete_translation_other_user(
        self,
        auth_client: TestClient,
        session: Session,
        test_profile: Profile,
    ) -> None:
        """TC-T-104: 타인 기록 삭제 시도 -> 404"""
        # 다른 사용자의 번역 기록 생성
        other_profile = Profile(
            id=uuid4(),
            user_id=uuid4(),
            display_name="OtherUser",
            preferred_language="en",
        )
        session.add(other_profile)
        session.commit()

        other_translation = Translation(
            id=uuid4(),
            profile_id=other_profile.id,
            source_text="Test",
            translated_text="테스트",
            source_lang="en",
            target_lang="ko",
            translation_type="text",
        )
        session.add(other_translation)
        session.commit()

        # 다른 사용자의 기록 삭제 시도
        response = auth_client.delete(f"/translations/{other_translation.id}")

        assert response.status_code == 404
