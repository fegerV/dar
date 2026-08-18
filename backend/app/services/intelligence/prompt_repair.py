from app.models.intelligence import VideoRecipe
from app.repositories.generations import GenerationRepository


class PromptRepairService:
    REPAIR_RULES = {
        "excessive_motion": {
            "prompt": "static camera, minimal motion, slow push-in",
            "negative": "fast camera movement, excessive motion, shaky",
        },
        "face_distortion": {
            "prompt": "stable face, frontal pose, neutral expression",
            "negative": "distorted face, morphing, extra limbs, artifacts",
        },
        "face_count_mismatch": {
            "prompt": "single person, frontal portrait",
            "negative": "multiple faces, crowd, group",
        },
        "low_face_quality": {
            "prompt": "high detail face, sharp features",
            "negative": "blurry face, low detail, noisy",
        },
        "prompt_non_adherence": {
            "prompt": "follow scene exactly, keep character pose",
            "negative": "ignore scene, change pose, drift",
        },
        "artifact": {
            "prompt": "clean render, photorealistic",
            "negative": "artifacts, glitch, noise, distortion",
        },
        "audio_issue": {
            "prompt": "clear speech, natural voice",
            "negative": "silence, noise, distorted audio",
        },
    }

    def __init__(self, db) -> None:
        self.db = db
        self.generation_repo = GenerationRepository(db)

    def repair(self, failure_codes: list[str], current_prompt: str | None, current_negative: str | None, recipe: VideoRecipe | None = None) -> dict:
        prompt_parts = []
        negative_parts = []

        for code in failure_codes:
            rule = self.REPAIR_RULES.get(code)
            if not rule:
                continue
            if rule["prompt"]:
                prompt_parts.append(rule["prompt"])
            if rule["negative"]:
                negative_parts.append(rule["negative"])

        base_prompt = (recipe.prompt if recipe and recipe.prompt else current_prompt) or ""
        base_negative = (recipe.negative_strategy if recipe and recipe.negative_strategy else current_negative) or ""

        repaired_prompt = self._merge_prompt(base_prompt, prompt_parts)
        repaired_negative = self._merge_negative(base_negative, negative_parts)

        return {
            "repaired_prompt": repaired_prompt,
            "repaired_negative": repaired_negative,
            "repair_rules_applied": [code for code in failure_codes if code in self.REPAIR_RULES],
        }

    def _merge_prompt(self, base: str, additions: list[str]) -> str:
        parts = [base.strip()] if base.strip() else []
        parts.extend([p for p in additions if p and p not in parts])
        return ", ".join(parts)

    def _merge_negative(self, base: str, additions: list[str]) -> str:
        parts = [base.strip()] if base.strip() else []
        parts.extend([p for p in additions if p and p not in parts])
        return ", ".join(parts)
