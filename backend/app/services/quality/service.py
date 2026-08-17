from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.generation import Generation
from app.repositories.quality import QualityRepository
from app.schemas.quality import (
    QualityCheckResponse,
    QualityGateResponse,
    QualityCheckRequest,
    ManualReviewRequest,
    ManualReviewResponse,
)


class QualityGateService:
    MIN_DURATION_SEC = 5
    MAX_DURATION_SEC = 300
    MIN_RESOLUTION = (720, 480)
    MAX_FPS = 60
    MIN_FPS = 24

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = QualityRepository(db)

    async def run_quality_checks(self, body: QualityCheckRequest) -> QualityGateResponse:
        generation = await self.repo.get_generation(body.generation_id)
        if generation is None:
            raise NotFoundException("Генерация не найдена")

        checks = {}
        passed = True

        for asset_id in body.asset_ids:
            asset_checks = await self._check_asset(asset_id, generation)
            checks[str(asset_id)] = asset_checks
            if not asset_checks["passed"]:
                passed = False

        output = generation.output_json or {}
        output["quality_checks"] = checks
        output["auto_checks_passed"] = passed
        await self.repo.update_generation_status(
            generation.id, "review", output_json=output
        )

        manual_review_required = not passed or generation.type in ("final", "video")

        return QualityGateResponse(
            generation_id=generation.id,
            status="review",
            auto_checks_passed=passed,
            manual_review_required=manual_review_required,
            final_status="approved" if passed and not manual_review_required else "pending_review",
            checks=[
                QualityCheckResponse(
                    id=UUID(int=0),
                    generation_id=generation.id,
                    asset_id=aid,
                    status="passed" if chk["passed"] else "failed",
                    checks=chk,
                    passed=chk["passed"],
                    created_at=datetime.now(timezone.utc),
                )
                for aid, chk in checks.items()
            ],
        )

    async def submit_manual_review(
        self, generation_id: UUID, body: ManualReviewRequest
    ) -> ManualReviewResponse:
        generation = await self.repo.get_generation(generation_id)
        if generation is None:
            raise NotFoundException("Генерация не найдена")

        final_status = "approved" if body.passed else "rejected"
        output = generation.output_json or {}
        output["manual_review"] = {
            "passed": body.passed,
            "comment": body.comment,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.repo.update_generation_status(generation.id, final_status, output_json=output)

        return ManualReviewResponse(
            id=UUID(int=0),
            generation_id=generation_id,
            status=final_status,
            passed=body.passed,
            review_comment=body.comment,
            reviewed_at=datetime.now(timezone.utc),
        )

    async def _check_asset(self, asset_id: UUID, generation: Generation) -> dict:
        checks = {}
        passed = True

        duration = generation.output_json.get("duration_sec") or 30
        if duration < self.MIN_DURATION_SEC or duration > self.MAX_DURATION_SEC:
            checks["duration"] = {
                "passed": False,
                "value": duration,
                "min": self.MIN_DURATION_SEC,
                "max": self.MAX_DURATION_SEC,
            }
            passed = False
        else:
            checks["duration"] = {"passed": True, "value": duration}

        resolution = generation.output_json.get("resolution") or (1280, 720)
        if isinstance(resolution, list):
            resolution = tuple(resolution)
        if resolution[0] < self.MIN_RESOLUTION[0] or resolution[1] < self.MIN_RESOLUTION[1]:
            checks["resolution"] = {
                "passed": False,
                "value": resolution,
                "min": self.MIN_RESOLUTION,
            }
            passed = False
        else:
            checks["resolution"] = {"passed": True, "value": resolution}

        audio_ok = generation.output_json.get("audio_ok", True)
        checks["audio"] = {"passed": audio_ok, "value": audio_ok}
        if not audio_ok:
            passed = False

        fps = generation.output_json.get("fps") or 30
        if fps < self.MIN_FPS or fps > self.MAX_FPS:
            checks["fps"] = {
                "passed": False,
                "value": fps,
                "min": self.MIN_FPS,
                "max": self.MAX_FPS,
            }
            passed = False
        else:
            checks["fps"] = {"passed": True, "value": fps}

        return {"passed": passed, "checks": checks}
