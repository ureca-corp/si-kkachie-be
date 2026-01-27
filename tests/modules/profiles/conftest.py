"""profiles 도메인 테스트 픽스처"""

import pytest
from sqlmodel import Session

from src.modules.profiles.models import Profile


@pytest.fixture
def profile_data() -> dict:
    """테스트용 프로필 데이터"""
    return {
        "display_name": "여행자",
        "preferred_language": "en",
    }


@pytest.fixture
def update_profile_data() -> dict:
    """프로필 수정 데이터"""
    return {
        "display_name": "새 이름",
        "preferred_language": "ko",
    }


@pytest.fixture
def profile_image_request() -> dict:
    """프로필 이미지 업로드 요청 데이터"""
    return {
        "file_name": "profile.jpg",
        "content_type": "image/jpeg",
    }
