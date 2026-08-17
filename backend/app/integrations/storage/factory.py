from app.core.config import settings
from app.integrations.storage.base import StorageProvider
from app.integrations.storage.minio import MinIOProvider
from app.integrations.storage.yandex_disk import YandexDiskProvider


def get_storage_provider() -> StorageProvider:
    provider = settings.STORAGE_PROVIDER.lower()
    if provider == "minio":
        return MinIOProvider()
    elif provider == "yandex":
        return YandexDiskProvider()
    else:
        raise ValueError(f"Unsupported storage provider: {provider}")
