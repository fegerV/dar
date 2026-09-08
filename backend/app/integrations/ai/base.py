from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class ProviderResult:
    """Результат выполнения запроса к провайдеру."""
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    provider_name: str | None = None


@dataclass
class FallbackChainConfig:
    """Конфигурация цепочки fallback для провайдера."""
    max_retries: int = 3
    timeout_seconds: float = 30.0
    fail_on_first_error: bool = False
    log_failures: bool = True


class BaseProvider(ABC):
    provider_id: UUID
    name: str
    enabled: bool = True
    priority: int = 0  # Приоритет провайдера (меньше = выше приоритет)

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
        self.text_providers.sort(key=lambda p: p.priority)

    def register_image(self, provider: BaseImageProvider) -> None:
        self.image_providers.append(provider)
        self.image_providers.sort(key=lambda p: p.priority)

    def register_video(self, provider: BaseVideoProvider) -> None:
        self.video_providers.append(provider)
        self.video_providers.sort(key=lambda p: p.priority)

    def register_voice(self, provider: BaseVoiceProvider) -> None:
        self.voice_providers.append(provider)
        self.voice_providers.sort(key=lambda p: p.priority)

    def register_music(self, provider: BaseMusicProvider) -> None:
        self.music_providers.append(provider)
        self.music_providers.sort(key=lambda p: p.priority)

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

    def _get_enabled_providers(self, providers: list) -> list:
        """Получить список включенных провайдеров, отсортированных по приоритету."""
        return [p for p in providers if p.enabled]

    async def execute_with_fallback(
        self,
        providers: list,
        execute_func: str,
        *args,
        config: FallbackChainConfig | None = None,
        **kwargs
    ) -> ProviderResult:
        """
        Выполнить операцию с цепочкой fallback.
        
        Args:
            providers: Список провайдеров для попытки выполнения
            execute_func: Имя метода для вызова (например, 'generate_text')
            *args: Позиционные аргументы для метода
            config: Конфигурация fallback цепочки
            **kwargs: Именованные аргументы для метода
            
        Returns:
            ProviderResult с результатом или ошибкой
        """
        import asyncio
        import logging
        
        logger = logging.getLogger(__name__)
        config = config or FallbackChainConfig()
        enabled_providers = self._get_enabled_providers(providers)
        
        if not enabled_providers:
            return ProviderResult(
                success=False,
                error="No enabled providers available"
            )
        
        last_error: Exception | None = None
        
        for idx, provider in enumerate(enabled_providers):
            if idx >= config.max_retries:
                break
                
            try:
                # Проверяем health перед использованием
                if not await provider.healthcheck():
                    if config.log_failures:
                        logger.warning(f"Provider {provider.name} healthcheck failed")
                    continue
                
                # Вызываем метод провайдера
                method = getattr(provider, execute_func, None)
                if method is None:
                    raise AttributeError(f"Method {execute_func} not found on {provider.name}")
                
                result = await asyncio.wait_for(
                    method(*args, **kwargs),
                    timeout=config.timeout_seconds
                )
                
                return ProviderResult(
                    success=True,
                    data=result,
                    provider_name=provider.name
                )
                
            except asyncio.TimeoutError as e:
                last_error = e
                if config.log_failures:
                    logger.warning(f"Provider {provider.name} timed out after {config.timeout_seconds}s")
                    
            except Exception as e:
                last_error = e
                if config.log_failures:
                    logger.exception(f"Provider {provider.name} failed: {e}")
                
                if config.fail_on_first_error:
                    return ProviderResult(
                        success=False,
                        error=str(e),
                        provider_name=provider.name
                    )
        
        # Все провайдеры исчерпаны
        return ProviderResult(
            success=False,
            error=f"All providers failed. Last error: {last_error}" if last_error else "All providers failed",
        )

    async def generate_text_with_fallback(
        self, 
        prompt: str, 
        parameters: dict[str, Any],
        config: FallbackChainConfig | None = None
    ) -> ProviderResult:
        """Выполнить генерацию текста с fallback цепочкой."""
        return await self.execute_with_fallback(
            self.text_providers,
            'generate_text',
            prompt,
            parameters,
            config=config
        )

    async def generate_image_with_fallback(
        self, 
        prompt: str, 
        parameters: dict[str, Any],
        config: FallbackChainConfig | None = None
    ) -> ProviderResult:
        """Выполнить генерацию изображения с fallback цепочкой."""
        return await self.execute_with_fallback(
            self.image_providers,
            'generate_image',
            prompt,
            parameters,
            config=config
        )

    async def generate_video_with_fallback(
        self, 
        prompt: str, 
        parameters: dict[str, Any],
        config: FallbackChainConfig | None = None
    ) -> ProviderResult:
        """Выполнить генерацию видео с fallback цепочкой."""
        return await self.execute_with_fallback(
            self.video_providers,
            'generate_video',
            prompt,
            parameters,
            config=config
        )

    async def generate_voice_with_fallback(
        self, 
        text: str, 
        parameters: dict[str, Any],
        config: FallbackChainConfig | None = None
    ) -> ProviderResult:
        """Выполнить генерацию голоса с fallback цепочкой."""
        return await self.execute_with_fallback(
            self.voice_providers,
            'generate_voice',
            text,
            parameters,
            config=config
        )

    async def generate_music_with_fallback(
        self, 
        prompt: str, 
        parameters: dict[str, Any],
        config: FallbackChainConfig | None = None
    ) -> ProviderResult:
        """Выполнить генерацию музыки с fallback цепочкой."""
        return await self.execute_with_fallback(
            self.music_providers,
            'generate_music',
            prompt,
            parameters,
            config=config
        )
