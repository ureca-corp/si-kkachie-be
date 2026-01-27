from src.external.storage.s3_provider import S3StorageProvider


class R2StorageProvider(S3StorageProvider):
    """Cloudflare R2 스토리지 공급자 (S3 API 호환)

    실제 사용 시 boto3 패키지 설치 필요:
    uv add boto3
    """

    def __init__(
        self,
        bucket: str,
        account_id: str,
        access_key: str,
        secret_key: str,
    ):
        super().__init__(
            bucket=bucket,
            region="auto",
            access_key=access_key,
            secret_key=secret_key,
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        )
