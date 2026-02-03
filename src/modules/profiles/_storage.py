"""profiles 스토리지 유틸리티

프로필 이미지 업로드를 위한 Supabase Storage 연동
"""

from uuid import UUID

from src.external.supabase import get_storage_provider


def create_presigned_url(
    profile_id: UUID,
    file_name: str,
    content_type: str,
) -> dict:
    """프로필 이미지 업로드용 presigned URL 생성

    Returns:
        upload_url: 파일 업로드용 URL
        public_url: 업로드 완료 후 공개 URL
        expires_in: URL 유효 시간 (초)
    """
    storage = get_storage_provider()

    if storage is None:
        # 스토리지 미설정 시 더미 URL 반환 (테스트용)
        return {
            "upload_url": "https://storage.supabase.co/presigned-url",
            "public_url": f"https://storage.supabase.co/public/profiles/{profile_id}/{file_name}",
            "expires_in": 3600,
        }

    # 실제 스토리지 사용
    path = f"profiles/{profile_id}/{file_name}"
    upload_url = storage.get_upload_url(key=path, expires_in=3600)
    public_url = f"{path}"  # 스토리지 provider에서 base URL 추가됨

    return {
        "upload_url": upload_url,
        "public_url": public_url,
        "expires_in": 3600,
    }


def get_public_url(profile_id: UUID, file_name: str) -> str:
    """프로필 이미지 공개 URL 조회"""
    storage = get_storage_provider()

    if storage is None:
        return f"https://storage.supabase.co/public/profiles/{profile_id}/{file_name}"

    return f"profiles/{profile_id}/{file_name}"
