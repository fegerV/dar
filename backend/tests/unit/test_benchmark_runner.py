"""Tests for benchmark runner service."""

from unittest.mock import AsyncMock

import pytest

from app.models.lab import LabScenario
from app.services.lab.models import (
    ModelConfig,
    estimate_generation_cost,
    get_model_config,
    list_benchmark_models,
)
from app.services.lab.runner import BenchmarkResult, BenchmarkRunner
from app.services.lab.seed_data import get_scenario_by_code, get_scenario_data


class TestModelConfig:
    def test_get_model_config(self):
        config = get_model_config("runway-gen3")
        assert config is not None
        assert config.name == "runway-gen3"
        assert config.display_name == "Runway Gen-3 Alpha"

    def test_get_model_config_unknown(self):
        config = get_model_config("unknown-model")
        assert config is None

    def test_list_benchmark_models(self):
        models = list_benchmark_models()
        assert len(models) == 4
        assert all(isinstance(m, ModelConfig) for m in models)

    def test_estimate_generation_cost(self):
        cost = estimate_generation_cost("runway-gen3", 5)
        assert cost > 0
        assert cost == 1.50 + (0.15 * 5)

    def test_estimate_generation_cost_unknown(self):
        cost = estimate_generation_cost("unknown", 5)
        assert cost == 0.05


class TestBenchmarkResult:
    def test_success_result(self):
        result = BenchmarkResult(
            success=True,
            quality_score=0.92,
            generation_time_sec=45.0,
            actual_cost=2.25,
        )
        assert result.success is True
        assert result.quality_score == 0.92
        assert result.error_message is None

    def test_failed_result(self):
        result = BenchmarkResult(
            success=False,
            error_message="Generation failed",
        )
        assert result.success is False
        assert result.quality_score == 0.0


class TestBenchmarkRunner:
    @pytest.mark.asyncio
    async def test_compile_prompt(self):
        from app.models.lab import LabScenario

        runner = BenchmarkRunner(AsyncMock())
        scenario = LabScenario(
            code="test",
            name="Test",
            prompt_template="A {difficulty} test with {camera} camera",
            difficulty="easy",
            target_camera="static",
        )
        prompt = runner._compile_prompt(scenario)
        assert "easy" in prompt
        assert "static" in prompt

    @pytest.mark.asyncio
    async def test_evaluate_quality(self):
        runner = BenchmarkRunner(AsyncMock())
        model_config = get_model_config("runway-gen3")

        result = await runner._execute_generation(
            LabScenario(
                code="test",
                name="Test",
                prompt_template="Test prompt",
                difficulty="easy",
            ),
            model_config,
        )
        assert isinstance(result, BenchmarkResult)


class TestSeedData:
    def test_get_scenario_data(self):
        scenarios = get_scenario_data()
        assert len(scenarios) == 15

    def test_scenario_codes_unique(self):
        scenarios = get_scenario_data()
        codes = [s["code"] for s in scenarios]
        assert len(codes) == len(set(codes))

    def test_get_scenario_by_code(self):
        scenario = get_scenario_by_code("portrait-talking")
        assert scenario is not None
        assert scenario["name"] == "Portrait Talking Head"

    def test_get_scenario_by_code_unknown(self):
        scenario = get_scenario_by_code("unknown")
        assert scenario is None

    def test_all_scenarios_have_required_fields(self):
        scenarios = get_scenario_data()
        required_fields = ["code", "name", "category", "difficulty", "prompt_template"]
        for scenario in scenarios:
            for field in required_fields:
                assert field in scenario, f"Missing {field} in {scenario['code']}"
