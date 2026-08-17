"""
Mock AI providers for development and testing.
"""
import uuid
from typing import Any, Optional

from ai_providers.base import (
    ImageProvider,
    VideoProvider,
    TTSProvider,
    MusicProvider,
    LLMProvider,
)


class MockImageProvider(ImageProvider):
    """Mock image provider for testing."""

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 50,
        **kwargs,
    ) -> dict:
        """Generate mock image."""
        task_id = f"img_{uuid.uuid4()}"
        return {
            "task_id": task_id,
            "status": "completed",
            "image_url": f"https://example.com/generated/{task_id}.png",
            "width": width,
            "height": height,
        }

    async def generate(self, prompt: str, **kwargs) -> Any:
        return await self.generate_image(prompt, **kwargs)

    async def check_status(self, task_id: str) -> dict:
        return {"task_id": task_id, "status": "completed"}

    async def cancel(self, task_id: str) -> bool:
        return True


class MockVideoProvider(VideoProvider):
    """Mock video provider for testing."""

    async def generate_video(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        duration: int = 5,
        fps: int = 24,
        **kwargs,
    ) -> dict:
        """Generate mock video."""
        task_id = f"vid_{uuid.uuid4()}"
        return {
            "task_id": task_id,
            "status": "completed",
            "video_url": f"https://example.com/generated/{task_id}.mp4",
            "duration": duration,
            "fps": fps,
        }

    async def generate(self, prompt: str, **kwargs) -> Any:
        return await self.generate_video(prompt, **kwargs)

    async def check_status(self, task_id: str) -> dict:
        return {"task_id": task_id, "status": "completed"}

    async def cancel(self, task_id: str) -> bool:
        return True


class MockTTSProvider(TTSProvider):
    """Mock TTS provider for testing."""

    async def generate_speech(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0,
        **kwargs,
    ) -> dict:
        """Generate mock speech."""
        task_id = f"tts_{uuid.uuid4()}"
        return {
            "task_id": task_id,
            "status": "completed",
            "audio_url": f"https://example.com/generated/{task_id}.mp3",
            "duration": len(text) * 0.1,
        }

    async def generate(self, prompt: str, **kwargs) -> Any:
        return await self.generate_speech(prompt, **kwargs)

    async def check_status(self, task_id: str) -> dict:
        return {"task_id": task_id, "status": "completed"}

    async def cancel(self, task_id: str) -> bool:
        return True


class MockMusicProvider(MusicProvider):
    """Mock music provider for testing."""

    async def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        style: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Generate mock music."""
        task_id = f"mus_{uuid.uuid4()}"
        return {
            "task_id": task_id,
            "status": "completed",
            "audio_url": f"https://example.com/generated/{task_id}.mp3",
            "duration": duration,
            "style": style,
        }

    async def generate(self, prompt: str, **kwargs) -> Any:
        return await self.generate_music(prompt, **kwargs)

    async def check_status(self, task_id: str) -> dict:
        return {"task_id": task_id, "status": "completed"}

    async def cancel(self, task_id: str) -> bool:
        return True


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Generate mock text."""
        return f"Generated response for: {prompt[:100]}..."

    async def compile_prompt(
        self,
        template: str,
        variables: dict,
        **kwargs,
    ) -> str:
        """Compile prompt template with variables."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    async def generate(self, prompt: str, **kwargs) -> Any:
        return await self.generate_text(prompt, **kwargs)

    async def check_status(self, task_id: str) -> dict:
        return {"task_id": task_id, "status": "completed"}

    async def cancel(self, task_id: str) -> bool:
        return True
