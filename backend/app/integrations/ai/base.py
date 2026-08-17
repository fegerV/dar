from abc import ABC, abstractmethod
from uuid import UUID
from typing import Any

class BaseProvider(ABC):
    provider_id: UUID
    name: str
    enabled: bool = True

    @abstractmethod
    async def healthcheck(self) -> bool:
        ...

    @abstractmethod
    def estimate_cost(self, task: dict[str, Any]) -> float:
        ...


class BaseTextProvider(BaseProvider):
    @abstractmethod
    async def generate_text(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        ...


class BaseImageProvider(BaseProvider):
    @abstractmethod
    async def generate_image(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        ...


class BaseVideoProvider(BaseProvider):
    @abstractmethod
    async def generate_video(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        ...


class BaseVoiceProvider(BaseProvider):
    @abstractmethod
    async def generate_voice(self, text: str, parameters: dict[str, Any]) -> dict[str, Any]:
        ...


class BaseMusicProvider(BaseProvider):
    @abstractmethod
    async def generate_music(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        ...


class ProviderRegistry:
    def __init__(self):
        self.text_providers: list[BaseTextProvider] = []
        self.image_providers: list[BaseImageProvider] = []
        self.video_providers: list[BaseVideoProvider] = []
        self.voice_providers: list[BaseVoiceProvider] = []
        self.music_providers: list[BaseMusicProvider] = []

    def register_text(self, provider: BaseTextProvider) -> None:
        self.text_providers.append(provider)

    def register_image(self, provider: BaseImageProvider) -> None:
        self.image_providers.append(provider)

    def register_video(self, provider: BaseVideoProvider) -> None:
        self.video_providers.append(provider)

    def register_voice(self, provider: BaseVoiceProvider) -> None:
        self.voice_providers.append(provider)

    def register_music(self, provider: BaseMusicProvider) -> None:
        self.music_providers.append(provider)

    def get_text(self) -> BaseTextProvider | None:
        return next((p for p in self.text_providers if p.enabled), None)

    def get_image(self) -> BaseImageProvider | None:
        return next((p for p in self.image_providers if p.enabled), None)

    def get_video(self) -> BaseVideoProvider | None:
        return next((p for p in self.video_providers if p.enabled), None)

    def get_voice(self) -> BaseVoiceProvider | None:
        return next((p for p in self.voice_providers if p.enabled), None)

    def get_music(self) -> BaseMusicProvider | None:
        return next((p for p in self.music_providers if p.enabled), None)
