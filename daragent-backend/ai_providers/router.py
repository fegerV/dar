"""
AI Provider Router - routes generation tasks to appropriate providers.
"""
from typing import Optional

from core.config import settings
from ai_providers.base import (
    ImageProvider,
    VideoProvider,
    TTSProvider,
    MusicProvider,
    LLMProvider,
)
from ai_providers.mock import (
    MockImageProvider,
    MockVideoProvider,
    MockTTSProvider,
    MockMusicProvider,
    MockLLMProvider,
)


class AIRouter:
    """
    Routes AI generation tasks to appropriate providers based on configuration.
    
    This allows switching between different AI providers without changing business logic.
    """

    def __init__(self):
        self._image_provider: Optional[ImageProvider] = None
        self._video_provider: Optional[VideoProvider] = None
        self._tts_provider: Optional[TTSProvider] = None
        self._music_provider: Optional[MusicProvider] = None
        self._llm_provider: Optional[LLMProvider] = None

    def get_image_provider(self) -> ImageProvider:
        """Get configured image provider."""
        if self._image_provider is None:
            self._image_provider = self._create_image_provider()
        return self._image_provider

    def get_video_provider(self) -> VideoProvider:
        """Get configured video provider."""
        if self._video_provider is None:
            self._video_provider = self._create_video_provider()
        return self._video_provider

    def get_tts_provider(self) -> TTSProvider:
        """Get configured TTS provider."""
        if self._tts_provider is None:
            self._tts_provider = self._create_tts_provider()
        return self._tts_provider

    def get_music_provider(self) -> MusicProvider:
        """Get configured music provider."""
        if self._music_provider is None:
            self._music_provider = self._create_music_provider()
        return self._music_provider

    def get_llm_provider(self) -> LLMProvider:
        """Get configured LLM provider."""
        if self._llm_provider is None:
            self._llm_provider = self._create_llm_provider()
        return self._llm_provider

    def _create_image_provider(self) -> ImageProvider:
        """Create image provider based on settings."""
        provider_type = settings.AI_IMAGE_PROVIDER.lower()
        
        if provider_type == "mock":
            return MockImageProvider()
        # elif provider_type == "replicate":
        #     return ReplicateImageProvider()
        # elif provider_type == "stability":
        #     return StabilityImageProvider()
        else:
            return MockImageProvider()

    def _create_video_provider(self) -> VideoProvider:
        """Create video provider based on settings."""
        provider_type = settings.AI_VIDEO_PROVIDER.lower()
        
        if provider_type == "mock":
            return MockVideoProvider()
        # elif provider_type == "replicate":
        #     return ReplicateVideoProvider()
        else:
            return MockVideoProvider()

    def _create_tts_provider(self) -> TTSProvider:
        """Create TTS provider based on settings."""
        provider_type = settings.AI_TTS_PROVIDER.lower()
        
        if provider_type == "mock":
            return MockTTSProvider()
        # elif provider_type == "elevenlabs":
        #     return ElevenLabsTTSProvider()
        # elif provider_type == "openai":
        #     return OpenAITTSProvider()
        else:
            return MockTTSProvider()

    def _create_music_provider(self) -> MusicProvider:
        """Create music provider based on settings."""
        provider_type = settings.AI_MUSIC_PROVIDER.lower()
        
        if provider_type == "mock":
            return MockMusicProvider()
        # elif provider_type == "suno":
        #     return SunoMusicProvider()
        else:
            return MockMusicProvider()

    def _create_llm_provider(self) -> LLMProvider:
        """Create LLM provider based on settings."""
        provider_type = settings.AI_LLM_PROVIDER.lower()
        
        if provider_type == "mock":
            return MockLLMProvider()
        # elif provider_type == "openai":
        #     return OpenAILLMProvider()
        # elif provider_type == "anthropic":
        #     return AnthropicLLMProvider()
        else:
            return MockLLMProvider()


# Global router instance
ai_router = AIRouter()
