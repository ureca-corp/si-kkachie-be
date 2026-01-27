from typing import BinaryIO

from src.external.storage.base import IStorageProvider


class SupabaseStorageProvider(IStorageProvider):
    """Supabase 스토리지 공급자 (스텁)

    실제 사용 시 supabase 패키지 설치 필요:
    uv add supabase
    """

    def __init__(self, url: str, key: str, bucket: str):
        from supabase import create_client

        self.client = create_client(url, key)
        self.bucket = bucket

    def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None,
    ) -> str:
        data = file.read()
        self.client.storage.from_(self.bucket).upload(key, data)
        return self.client.storage.from_(self.bucket).get_public_url(key)

    def download(self, key: str) -> bytes:
        return self.client.storage.from_(self.bucket).download(key)

    def delete(self, key: str) -> bool:
        self.client.storage.from_(self.bucket).remove([key])
        return True

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        result = self.client.storage.from_(self.bucket).create_signed_url(
            key,
            expires_in,
        )
        return result["signedURL"]

    def get_upload_url(self, key: str, expires_in: int = 3600) -> str:
        result = self.client.storage.from_(self.bucket).create_signed_upload_url(key)
        return result["signedURL"]
