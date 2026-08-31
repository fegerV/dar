"""Polza.ai API integration service."""

import time
from typing import Any

import httpx

from app.models.admin import AIModel, AIProvider


class PolzaAIService:
    """Service for interacting with Polza.ai API."""

    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.base_url = provider.base_url.rstrip("/")
        self.api_key = provider.api_key_encrypted

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_image(
        self,
        model: AIModel,
        prompt: str,
        aspect_ratio: str = "auto",
        image_resolution: str = "1K",
        images: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Generate or edit an image using Polza.ai Media API."""
        input_data: dict[str, Any] = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "image_resolution": image_resolution,
        }
        if images:
            input_data["images"] = images

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/media",
                headers=self._headers(),
                json={
                    "model": model.model_id,
                    "input": input_data,
                },
            )
            response.raise_for_status()
            return response.json()

    async def generate_video(
        self,
        model: AIModel,
        prompt: str,
        aspect_ratio: str = "auto",
        duration: int = 8,
        resolution: str = "480p",
        images: list[dict[str, str]] | None = None,
        generate_audio: bool = False,
        videos: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Generate a video using Polza.ai Media API."""
        input_data: dict[str, Any] = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "resolution": resolution,
        }
        if images:
            input_data["images"] = images
        if generate_audio:
            input_data["generate_audio"] = "true" if generate_audio else "false"
        if videos:
            input_data["videos"] = videos

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/media",
                headers=self._headers(),
                json={
                    "model": model.model_id,
                    "input": input_data,
                },
            )
            response.raise_for_status()
            return response.json()

    async def chat(
        self,
        model: AIModel,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Send a chat completion request."""
        payload: dict[str, Any] = {
            "model": model.model_id,
            "input": {
                "messages": messages,
                "temperature": temperature,
            },
        }
        if max_tokens:
            payload["input"]["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/media",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> tuple[bool, str, int]:
        """Check if the provider is healthy. Returns (ok, message, latency_ms)."""
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._headers(),
                )
                latency_ms = int((time.time() - start) * 1000)
                if response.status_code == 200:
                    return True, "Connection successful", latency_ms
                return False, f"HTTP {response.status_code}", latency_ms
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            return False, str(e), latency_ms


async def get_polza_service(provider: AIProvider) -> PolzaAIService:
    """Factory function to create PolzaAIService."""
    return PolzaAIService(provider)
