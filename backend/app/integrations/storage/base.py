from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    @abstractmethod
    async def upload(
        self,
        bucket: str,
        object_key: str,
        data: BinaryIO,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        ...

    @abstractmethod
    async def download(self, bucket: str, object_key: str) -> bytes:
        ...

    @abstractmethod
    async def delete(self, bucket: str, object_key: str) -> bool:
        ...

    @abstractmethod
    async def generate_presigned_url(
        self,
        bucket: str,
        object_key: str,
        expires_in: int = 900,
        method: str = "GET",
    ) -> str:
        ...

    @abstractmethod
    async def generate_presigned_upload_url(
        self,
        bucket: str,
        object_key: str,
        expires_in: int = 900,
        content_type: str | None = None,
    ) -> str:
        ...

    @abstractmethod
    async def healthcheck(self) -> bool:
        ...
