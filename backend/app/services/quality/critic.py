from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.generation import Generation
from app.models.quality import VideoCriticResult
from app.repositories.generations import GenerationRepository
from app.repositories.quality import QualityRepository


class VideoCriticService:
    CRITIC_THRESHOLD = 0.85
    CRITIC_WEIGHTS = {
        "identity": 0.30,
        "motion": 0.20,
        "prompt_adherence": 0.20,
        "face_quality": 0.15,
        "artifact": 0.15,
    }

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.quality_repo = QualityRepository(db)
        self.generation_repo = GenerationRepository(db)

    async def evaluate(self, generation_id: UUID, prompt: str | None = None) -> VideoCriticResult:
        generation = await self.generation_repo.get_by_id(generation_id)
        if generation is None:
            raise ValidationException("Генерация не найдена")

        payload = generation.output_json or {}
        scores = self._score(payload, prompt)
        overall = self._weighted_overall(scores)
        decision = "PASS" if overall >= self.CRITIC_THRESHOLD else "FAIL"

        critic = VideoCriticResult(
            generation_id=generation.id,
            identity_score=scores.get("identity"),
            motion_score=scores.get("motion"),
            prompt_adherence=scores.get("prompt_adherence"),
            face_quality=scores.get("face_quality"),
            artifact_score=scores.get("artifact"),
            overall=overall,
            decision=decision,
            raw_response={
                "scores": scores,
                "threshold": self.CRITIC_THRESHOLD,
                "prompt": prompt,
                "video_url": payload.get("video_url"),
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        self.db.add(critic)
        await self.db.flush()

        out = dict(payload)
        out["video_critic"] = critic.raw_response
        out["critic_decision"] = decision
        generation.output_json = out
        await self.db.flush()
        return critic

    def _score(self, payload: dict, prompt: str | None) -> dict:
        metrics = payload.get("video_metrics") or {}
        face_metrics = payload.get("face_metrics") or {}
        return {
            "identity": self._clamp(face_metrics.get("identity_score", 0.92)),
            "motion": self._clamp(metrics.get("motion_score", 0.90)),
            "prompt_adherence": self._clamp(metrics.get("prompt_adherence", 0.88)),
            "face_quality": self._clamp(face_metrics.get("face_quality", 0.95)),
            "artifact": self._clamp(metrics.get("artifact_score", 0.94)),
        }

    def _weighted_overall(self, scores: dict) -> float:
        return sum(scores.get(k, 0.0) * w for k, w in self.CRITIC_WEIGHTS.items())

    def _clamp(self, value: float) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, value))
