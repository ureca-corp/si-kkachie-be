from typing import TYPE_CHECKING, BinaryIO

from src.external.storage.base import IStorageProvider

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class S3StorageProvider(IStorageProvider):
    """AWS S3 스토리지 공급자

    실제 사용 시 boto3 패키지 설치 필요:
    uv add boto3
    """

    def __init__(
        self,
        bucket: str,
        region: str,
        access_key: str,
        secret_key: str,
        endpoint_url: str | None = None,
    ):
        import boto3

        self.bucket = bucket
        self.client: S3Client = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
        )

    def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None,
    ) -> str:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        self.client.upload_fileobj(file, self.bucket, key, ExtraArgs=extra_args)
        return f"s3://{self.bucket}/{key}"

    def download(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def delete(self, key: str) -> bool:
        self.client.delete_object(Bucket=self.bucket, Key=key)
        return True

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def get_upload_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
