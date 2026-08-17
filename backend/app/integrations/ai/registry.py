from app.integrations.ai.base import ProviderRegistry
from app.integrations.ai.grok_provider import GrokTextProvider
from app.integrations.ai.mock_providers import (
    MockImageProvider,
    MockMusicProvider,
    MockVideoProvider,
    MockVoiceProvider,
)


def create_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_text(GrokTextProvider())
    registry.register_image(MockImageProvider())
    registry.register_video(MockVideoProvider())
    registry.register_voice(MockVoiceProvider())
    registry.register_music(MockMusicProvider())
    return registry
