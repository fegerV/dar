import io
from typing import BinaryIO

import httpx

from app.core.config import settings
from app.integrations.storage.base import StorageProvider


class YandexDiskProvider(StorageProvider):
    def __init__(self) -> None:
        self.oauth_token = settings.YANDEX_DISK_OAUTH_TOKEN
        self.base_path = settings.YANDEX_DISK_BASE_PATH
        self.base_url = "https://cloud-api.yandex.net/v1/disk"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"OAuth {self.oauth_token}",
            "Accept": "application/json",
        }

    async def upload(
        self,
        bucket: str,
        object_key: str,
        data: BinaryIO,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        path = f"{self.base_path}/{bucket}/{object_key}"
        upload_url = None
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.base_url}/resources/upload",
                headers=self._headers(),
                params={"path": path, "overwrite": "true"},
                timeout=30,
            )
            resp.raise_for_status()
            upload_url = resp.json().get("href")

        if not upload_url:
            raise RuntimeError("Yandex Disk upload URL not received")

        async with httpx.AsyncClient() as client:
            upload_resp = await client.put(
                upload_url,
                content=data.read(),
                headers={"Content-Type": content_type or "application/octet-stream"},
                timeout=60,
            )
            upload_resp.raise_for_status()

        return f"yd://{path}"

    async def download(self, bucket: str, object_key: str) -> bytes:
        path = f"{self.base_path}/{bucket}/{object_key}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/resources/download",
                headers=self._headers(),
                params={"path": path},
                timeout=30,
            )
            resp.raise_for_status()
            download_url = resp.json().get("href")

        if not download_url:
            raise RuntimeError("Yandex Disk download URL not received")

        async with httpx.AsyncClient() as client:
            file_resp = await client.get(download_url, timeout=60)
            file_resp.raise_for_status()
            return file_resp.content

    async def delete(self, bucket: str, object_key: str) -> bool:
        path = f"{self.base_path}/{bucket}/{object_key}"
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.base_url}/resources",
                headers=self._headers(),
                params={"path": path, "permanently": "true"},
                timeout=30,
            )
            if resp.status_code == 404:
                return True
            resp.raise_for_status()
        return True

    async def generate_presigned_url(
        self,
        bucket: str,
        object_key: str,
        expires_in: int = 900,
        method: str = "GET",
    ) -> str:
        path = f"{self.base_path}/{bucket}/{object_key}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/resources/download",
                headers=self._headers(),
                params={"path": path},
                timeout=30,
            )
            resp.raise_for_status()
            download_url = resp.json().get("href")
        if not download_url:
            raise RuntimeError("Yandex Disk presigned URL not received")
        return download_url

    async def generate_presigned_upload_url(
        self,
        bucket: str,
        object_key: str,
        expires_in: int = 900,
        content_type: str | None = None,
    ) -> str:
        path = f"{self.base_path}/{bucket}/{object_key}"
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.base_url}/resources/upload",
                headers=self._headers(),
                params={"path": path, "overwrite": "true"},
                timeout=30,
            )
            resp.raise_for_status()
            upload_url = resp.json().get("href")
        if not upload_url:
            raise RuntimeError("Yandex Disk upload URL not received")
        return upload_url
