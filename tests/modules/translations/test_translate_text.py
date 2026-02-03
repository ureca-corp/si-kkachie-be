"""POST /translate/text 테스트

SPEC 기반 테스트 케이스:
- TC-T-001: 텍스트 번역 (한->영)
- TC-T-002: 텍스트 번역 (영->한)
- TC-T-006: 대용량 텍스트 번역
- TC-T-101: 빈 텍스트
- TC-T-102: 같은 언어 번역
- TC-T-105: 텍스트 길이 초과
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.modules.profiles import Profile


class TestTranslateText:
    """POST /translate/text 테스트"""

    def test_translate_text_ko_to_en_success(
        self,
        auth_client: TestClient,
        test_profile: Profile,
        text_translation_request: dict,
    ) -> None:
        """TC-T-001: 텍스트 번역 (한->영) 성공"""
        with patch(
            "src.modules.translations._translation_service.TranslationService.translate"
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
            "src.modules.translations._translation_service.TranslationService.translate"
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
            "src.modules.translations._translation_service.TranslationService.translate"
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
