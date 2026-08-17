"""
AI Provider abstraction layer.

This module provides a unified interface for different AI providers,
allowing easy switching between providers without changing business logic.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class AIProvider(ABC):
    """Base abstract class for all AI providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Any:
        """Generate content based on prompt."""
        pass

    @abstractmethod
    async def check_status(self, task_id: str) -> dict:
        """Check generation status."""
        pass

    @abstractmethod
    async def cancel(self, task_id: str) -> bool:
        """Cancel generation task."""
        pass


class ImageProvider(AIProvider):
    """Image generation provider interface."""

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 50,
        **kwargs,
    ) -> dict:
        """Generate image from prompt."""
        pass


class VideoProvider(AIProvider):
    """Video generation provider interface."""

    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        duration: int = 5,
        fps: int = 24,
        **kwargs,
    ) -> dict:
        """Generate video from prompt or image."""
        pass


class TTSProvider(AIProvider):
    """Text-to-Speech provider interface."""

    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0,
        **kwargs,
    ) -> dict:
        """Generate speech from text."""
        pass


class MusicProvider(AIProvider):
    """Music generation provider interface."""

    @abstractmethod
    async def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        style: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Generate music from prompt."""
        pass


class LLMProvider(AIProvider):
    """LLM provider interface for text generation and prompt compilation."""

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    async def compile_prompt(
        self,
        template: str,
        variables: dict,
        **kwargs,
    ) -> str:
        """Compile prompt template with variables."""
        pass
