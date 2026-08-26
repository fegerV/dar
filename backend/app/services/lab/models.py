"""Model registry for benchmark runner.

Maps model names to their configurations, providers, and cost structures.
"""

from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for a video generation model."""

    name: str
    version: str
    display_name: str
    provider_type: str
    supported_resolutions: list[str]
    max_duration_sec: int
    cost_per_second: float
    cost_per_generation: float
    supports_image_input: bool
    supports_camera_control: bool
    supports_motion_control: bool
    avg_generation_time_sec: float
    quality_baseline: float
    speed_baseline: float
    reliability_baseline: float
    tags: list[str]


BENCHMARK_MODELS: dict[str, ModelConfig] = {
    "runway-gen3": ModelConfig(
        name="runway-gen3",
        version="v1",
        display_name="Runway Gen-3 Alpha",
        provider_type="runway",
        supported_resolutions=["1280x768", "768x1280"],
        max_duration_sec=10,
        cost_per_second=0.15,
        cost_per_generation=1.50,
        supports_image_input=True,
        supports_camera_control=True,
        supports_motion_control=True,
        avg_generation_time_sec=45.0,
        quality_baseline=0.92,
        speed_baseline=0.65,
        reliability_baseline=0.88,
        tags=["premium", "high-quality", "slow"],
    ),
    "kling-1.6": ModelConfig(
        name="kling-1.6",
        version="v1",
        display_name="Kling 1.6",
        provider_type="kling",
        supported_resolutions=["1920x1080", "1080x1920", "1280x720"],
        max_duration_sec=5,
        cost_per_second=0.10,
        cost_per_generation=0.50,
        supports_image_input=True,
        supports_camera_control=True,
        supports_motion_control=True,
        avg_generation_time_sec=30.0,
        quality_baseline=0.89,
        speed_baseline=0.75,
        reliability_baseline=0.90,
        tags=["balanced", "fast", "good-quality"],
    ),
    "pika-2.0": ModelConfig(
        name="pika-2.0",
        version="v1",
        display_name="Pika 2.0",
        provider_type="pika",
        supported_resolutions=["1080x1080", "1920x1080"],
        max_duration_sec=4,
        cost_per_second=0.08,
        cost_per_generation=0.32,
        supports_image_input=True,
        supports_camera_control=False,
        supports_motion_control=True,
        avg_generation_time_sec=20.0,
        quality_baseline=0.82,
        speed_baseline=0.85,
        reliability_baseline=0.85,
        tags=["fast", "cheap", "social-media"],
    ),
    "stable-video": ModelConfig(
        name="stable-video",
        version="v1",
        display_name="Stable Video Diffusion",
        provider_type="stability",
        supported_resolutions=["1024x576", "576x1024"],
        max_duration_sec=4,
        cost_per_second=0.05,
        cost_per_generation=0.20,
        supports_image_input=True,
        supports_camera_control=False,
        supports_motion_control=False,
        avg_generation_time_sec=25.0,
        quality_baseline=0.78,
        speed_baseline=0.80,
        reliability_baseline=0.82,
        tags=["cheap", "open-source", "experimental"],
    ),
}


def get_model_config(model_name: str) -> ModelConfig | None:
    """Get model configuration by name."""
    return BENCHMARK_MODELS.get(model_name)


def list_benchmark_models() -> list[ModelConfig]:
    """List all benchmark models."""
    return list(BENCHMARK_MODELS.values())


def estimate_generation_cost(model_name: str, duration_sec: int) -> float:
    """Estimate cost for a generation."""
    config = get_model_config(model_name)
    if not config:
        return 0.05
    return config.cost_per_generation + (config.cost_per_second * duration_sec)
