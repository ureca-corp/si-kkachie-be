"""profiles 도메인 Service"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Session

from src.core.enums import PreferredLanguage
from src.core.exceptions import NotFoundError
from src.external.storage import get_storage_provider

from . import repository
from .entities import ProfileImageUploadRequest, UpdateProfileRequest
from .models import Profile


def _utcnow() -> datetime:
    return datetime.now(UTC)


def verify_token_and_get_or_create_profile(
    session: Session,
    supabase_user_id: UUID,
    email: str,
) -> tuple[Profile, bool]:
    """토큰 검증 후 프로필 조회 또는 생성

    Returns:
        (Profile, is_new_user)
    """
    # 기존 프로필 조회
    profile = repository.get_by_user_id(session, supabase_user_id)

    if profile:
        return profile, False

    # 신규 프로필 생성
    new_profile = Profile(
        id=uuid4(),
        user_id=supabase_user_id,
        display_name=None,
        preferred_language=PreferredLanguage.EN.value,
        profile_image_url=None,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    created_profile = repository.create(session, new_profile)
    return created_profile, True


def get_profile_by_user_id(session: Session, user_id: UUID) -> Profile:
    """user_id로 프로필 조회"""
    profile = repository.get_by_user_id(session, user_id)
    if not profile:
        raise NotFoundError("프로필을 찾을 수 없어요")
    return profile


def update_profile(
    session: Session,
    profile: Profile,
    request: UpdateProfileRequest,
) -> Profile:
    """프로필 수정"""
    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(profile, key, value)

    profile.updated_at = _utcnow()
    return repository.update(session, profile)


def create_profile_image_upload_url(
    profile: Profile,
    request: ProfileImageUploadRequest,
) -> dict:
    """프로필 이미지 업로드 URL 생성"""
    storage = get_storage_provider()

    if storage is None:
        # 스토리지 미설정 시 더미 URL 반환 (테스트용)
        return {
            "upload_url": "https://storage.supabase.co/presigned-url",
            "public_url": f"https://storage.supabase.co/public/profiles/{profile.id}/{request.file_name}",
            "expires_in": 3600,
        }

    # 실제 스토리지 사용
    path = f"profiles/{profile.id}/{request.file_name}"
    upload_url = storage.get_upload_url(key=path, expires_in=3600)
    public_url = f"{path}"  # 스토리지 provider에서 base URL 추가됨

    return {
        "upload_url": upload_url,
        "public_url": public_url,
        "expires_in": 3600,
    }


def delete_profile(session: Session, profile: Profile) -> None:
    """프로필 삭제 (회원 탈퇴)"""
    repository.delete(session, profile)
