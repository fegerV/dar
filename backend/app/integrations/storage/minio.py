from io import BytesIO
from pathlib import Path
from uuid import UUID

try:
    from minio import Minio
    from minio.error import S3Error
except ImportError:
    Minio = None
    S3Error = Exception

from app.core.config import settings
from app.integrations.storage.base import StorageProvider


class MinIOProvider(StorageProvider):
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.secure = settings.MINIO_SECURE
        self.bucket = settings.MINIO_BUCKET
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error:
            pass

    async def upload(
        self,
        bucket: str,
        object_key: str,
        data: BinaryIO,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        bucket = bucket or self.bucket
        data_bytes = data.read() if hasattr(data, "read") else data
        self.client.put_object(
            bucket,
            object_key,
            BytesIO(data_bytes),
            length=len(data_bytes),
            content_type=content_type,
            metadata=metadata or {},
        )
        return f"{bucket}/{object_key}"

    async def download(self, bucket: str, object_key: str) -> bytes:
        bucket = bucket or self.bucket
        response = self.client.get_object(bucket, object_key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    async def delete(self, bucket: str, object_key: str) -> bool:
        bucket = bucket or self.bucket
        try:
            self.client.remove_object(bucket, object_key)
            return True
        except S3Error:
            return False

    async def generate_presigned_url(
        self,
        bucket: str,
        object_key: str,
        expires_in: int = 900,
        method: str = "GET",
    ) -> str:
        bucket = bucket or self.bucket
        return self.client.presigned_get_object(
            bucket,
            object_key,
            expires=expires_in,
        )

    async def generate_presigned_upload_url(
        self,
        bucket: str,
        object_key: str,
        expires_in: int = 900,
        content_type: str | None = None,
    ) -> str:
        bucket = bucket or self.bucket
        return self.client.presigned_put_object(
            bucket,
            object_key,
            expires=expires_in,
        )

    async def healthcheck(self) -> bool:
        try:
            self.client.bucket_exists(self.bucket)
            return True
        except Exception:
            return False
