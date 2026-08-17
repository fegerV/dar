from pathlib import Path
from uuid import UUID

from app.core.config import settings
from app.integrations.storage.base import StorageProvider


class YandexDiskProvider(StorageProvider):
    def __init__(self):
        self.oauth_token = settings.YANDEX_DISK_OAUTH_TOKEN
        self.base_path = settings.YANDEX_DISK_BASE_PATH
        self.base_url = "https://cloud-api.yandex.net/v1/disk"

    async def upload(
        self,
        bucket: str,
        object_key: str,
        data: BinaryIO,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        raise NotImplementedError("Yandex Disk upload not implemented yet")

    async def download(self, bucket: str, object_key: str) -> bytes:
        raise NotImplementedError("Yandex Disk download not implemented yet")

    async def delete(self, bucket: str, object_key: str) -> bool:
        raise NotImplementedError("Yandex Disk delete not implemented yet")

    async def generate_presigned_url(
        self,
        bucket: str,
        object_key: str,
        expires_in: int = 900,
        method: str = "GET",
    ) -> str:
        raise NotImplementedError("Yandex Disk presigned URL not implemented yet")

    async def generate_presigned_upload_url(
        self,
        bucket: str,
        object_key: str,
        expires_in: int = 900,
        content_type: str | None = None,
    ) -> str:
        raise NotImplementedError("Yandex Disk upload URL not implemented yet")
