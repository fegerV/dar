from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ai.registry import create_provider_registry


class AIOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.registry = create_provider_registry()

    async def generate_script(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        provider = self.registry.get_text()
        if provider is None:
            return {"text": None, "error": "No text provider available"}
        return await provider.generate_text(prompt, parameters)

    async def generate_image(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        provider = self.registry.get_image()
        if provider is None:
            return {"url": None, "error": "No image provider available"}
        return await provider.generate_image(prompt, parameters)

    async def generate_video(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        provider = self.registry.get_video()
        if provider is None:
            return {"url": None, "error": "No video provider available"}
        return await provider.generate_video(prompt, parameters)

    async def generate_voice(self, text: str, parameters: dict[str, Any]) -> dict[str, Any]:
        provider = self.registry.get_voice()
        if provider is None:
            return {"url": None, "error": "No voice provider available"}
        return await provider.generate_voice(text, parameters)

    async def generate_music(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        provider = self.registry.get_music()
        if provider is None:
            return {"url": None, "error": "No music provider available"}
        return await provider.generate_music(prompt, parameters)
