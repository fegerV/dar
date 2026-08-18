from sqlalchemy import select

from app.models.intelligence import ModelProfile, VideoRecipe
from app.repositories.generations import GenerationRepository


class RecipeService:
    def __init__(self, db) -> None:
        self.db = db
        self.generation_repo = GenerationRepository(db)

    async def get_best_recipe(self, template_code: str, input_metadata: dict | None = None) -> VideoRecipe | None:
        query = (
            select(VideoRecipe)
            .where(VideoRecipe.template_code == template_code)
            .where(VideoRecipe.is_active == 1)
            .order_by(VideoRecipe.success_rate.desc().nullslast(), VideoRecipe.avg_generations.asc().nullslast())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_recipe_stats(self, recipe_id, success: bool, generations_used: int, cost: float | None = None) -> None:
        recipe = await self.db.get(VideoRecipe, recipe_id)
        if not recipe:
            return
        total = (recipe.meta.get("total_generations") or 0) + 1
        successes = (recipe.meta.get("successes") or 0) + (1 if success else 0)
        recipe.success_rate = successes / total if total else None
        recipe.avg_generations = ((recipe.avg_generations or 1.0) * (total - 1) + generations_used) / total
        recipe.meta = dict(recipe.meta or {})
        recipe.meta["total_generations"] = total
        recipe.meta["successes"] = successes
        await self.db.flush()


class ModelSelectorService:
    def __init__(self, db) -> None:
        self.db = db
        self.recipe_service = RecipeService(db)

    async def select_model(self, template_code: str, input_metadata: dict | None = None) -> str | None:
        recipe = await self.recipe_service.get_best_recipe(template_code, input_metadata)
        if recipe:
            return recipe.model_name
        return self._fallback_model(input_metadata)

    def _fallback_model(self, input_metadata: dict | None) -> str | None:
        if not input_metadata:
            return "grok"
        if input_metadata.get("face_count", 1) > 1:
            return "kling"
        if input_metadata.get("pose") == "profile":
            return "veo"
        return "grok"


class FailureAnalyzer:
    CRITIC_TO_FAILURES = {
        "identity_score": ["face_distortion", "low_face_quality"],
        "motion_score": ["excessive_motion"],
        "prompt_adherence": ["prompt_non_adherence"],
        "face_quality": ["face_distortion", "low_face_quality"],
        "artifact_score": ["artifact"],
    }

    def analyze(self, critic: dict, quality_checks: dict) -> list[str]:
        failures = []
        scores = critic.get("scores", {})
        for metric, threshold in [("identity_score", 0.85), ("motion_score", 0.8), ("prompt_adherence", 0.8), ("face_quality", 0.85), ("artifact_score", 0.85)]:
            value = scores.get(metric)
            if isinstance(value, (int, float)) and value < threshold:
                failures.extend(self.CRITIC_TO_FAILURES.get(metric, []))

        checks = quality_checks.get("checks", {}) if isinstance(quality_checks, dict) else {}
        if checks.get("face_count", {}).get("passed") is False:
            failures.append("face_count_mismatch")
        if checks.get("semantic", {}).get("passed") is False:
            failures.append("prompt_non_adherence")
        if checks.get("audio", {}).get("passed") is False:
            failures.append("audio_issue")
        return list(set(failures))
