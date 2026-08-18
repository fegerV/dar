import hashlib
from typing import Any
from uuid import UUID

from app.integrations.ai.base import BaseImageProvider, BaseVideoProvider, BaseVoiceProvider, BaseMusicProvider


class MockImageProvider(BaseImageProvider):
    provider_id: UUID = UUID(int=0)

    def __init__(self):
        self.name = "mock_image"
        self.enabled = True

    async def healthcheck(self) -> bool:
        return True

    def estimate_cost(self, task: dict[str, Any]) -> float:
        return 0.0

    async def generate_image(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return {
            "url": f"https://example.com/mock-image/{hashlib.md5(prompt.encode()).hexdigest()}.png",
            "mime_type": "image/png",
            "width": parameters.get("width", 1024),
            "height": parameters.get("height", 1024),
        }


class MockVideoProvider(BaseVideoProvider):
    provider_id: UUID = UUID(int=0)

    def __init__(self):
        self.name = "mock_video"
        self.enabled = True

    async def healthcheck(self) -> bool:
        return True

    def estimate_cost(self, task: dict[str, Any]) -> float:
        return 0.0

    async def generate_video(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return {
            "url": f"https://example.com/mock-video/{hashlib.md5(prompt.encode()).hexdigest()}.mp4",
            "mime_type": "video/mp4",
            "duration_sec": parameters.get("duration_sec", 30),
            "width": parameters.get("width", 1920),
            "height": parameters.get("height", 1080),
            "fps": parameters.get("fps", 30),
        }


class MockVoiceProvider(BaseVoiceProvider):
    provider_id: UUID = UUID(int=0)

    def __init__(self):
        self.name = "mock_voice"
        self.enabled = True

    async def healthcheck(self) -> bool:
        return True

    def estimate_cost(self, task: dict[str, Any]) -> float:
        return 0.0

    async def generate_voice(self, text: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return {
            "url": f"https://example.com/mock-voice/{hashlib.md5(text.encode()).hexdigest()}.mp3",
            "mime_type": "audio/mpeg",
            "duration_sec": len(text) / 15.0,
        }


class MockMusicProvider(BaseMusicProvider):
    provider_id: UUID = UUID(int=0)

    def __init__(self):
        self.name = "mock_music"
        self.enabled = True

    async def healthcheck(self) -> bool:
        return True

    def estimate_cost(self, task: dict[str, Any]) -> float:
        return 0.0

    async def generate_music(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return {
            "url": f"https://example.com/mock-music/{hashlib.md5(prompt.encode()).hexdigest()}.mp3",
            "mime_type": "audio/mpeg",
            "duration_sec": parameters.get("duration_sec", 60),
        }
