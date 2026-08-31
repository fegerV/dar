from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.generation import Generation
from app.models.quality import QualityCheck, VideoCriticResult
from app.repositories.generations import GenerationRepository
from app.repositories.quality import QualityRepository
from app.schemas.quality import (
    ManualReviewRequest,
    ManualReviewResponse,
    QualityCheckRequest,
    QualityCheckResponse,
    QualityGateResponse,
    VideoCriticResponse,
)
from app.services.quality.critic import VideoCriticService


class QualityGateService:
    MIN_DURATION_SEC = 5
    MAX_DURATION_SEC = 300
    MIN_RESOLUTION = (720, 480)
    MAX_FPS = 60
    MIN_FPS = 24
    MAX_RETRIES = 3
    CRITIC_THRESHOLD = 0.85

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = QualityRepository(db)
        self.generation_repo = GenerationRepository(db)
        self.critic = VideoCriticService(db)

    async def run_quality_checks(self, body: QualityCheckRequest) -> QualityGateResponse:
        generation = await self.repo.get_generation(body.generation_id)
        if generation is None:
            raise NotFoundException("Генерация не найдена")

        checks: dict[str, dict] = {}
        passed = True
        for asset_id in body.asset_ids:
            asset_checks = await self._check_asset(asset_id, generation)
            checks[str(asset_id)] = asset_checks
            if not asset_checks["passed"]:
                passed = False

        critic = await self.critic.evaluate(generation.id, body.prompt if hasattr(body, "prompt") else None)
        critic_ok = critic.decision == "PASS"
        overall_ok = passed and critic_ok

        output = generation.output_json or {}
        output["quality_checks"] = checks
        output["auto_checks_passed"] = passed
        output["video_critic"] = critic.raw_response
        output["critic_decision"] = critic.decision

        await self.repo.update_generation_status(
            generation.id,
            "review",
            output_json=output,
        )
        await self._store_checks(generation.id, checks, critic)

        attempt = (generation.output_json or {}).get("quality_attempt") or 1
        if not overall_ok and attempt < self.MAX_RETRIES:
            output["quality_attempt"] = attempt + 1
            await self.generation_repo.update(generation)
            return QualityGateResponse(
                generation_id=generation.id,
                status="review",
                auto_checks_passed=overall_ok,
                manual_review_required=True,
                final_status="retry",
                checks=[
                    QualityCheckResponse(
                        id=UUID(int=0),
                        generation_id=generation.id,
                        asset_id=UUID(asset_id),
                        status="passed" if chk["passed"] else "failed",
                        checks=chk,
                        passed=chk["passed"],
                        created_at=datetime.now(UTC),
                    )
                    for asset_id, chk in checks.items()
                ],
                critic=VideoCriticResponse(
                    id=critic.id,
                    generation_id=critic.generation_id,
                    identity_score=critic.identity_score,
                    motion_score=critic.motion_score,
                    prompt_adherence=critic.prompt_adherence,
                    face_quality=critic.face_quality,
                    artifact_score=critic.artifact_score,
                    overall=critic.overall,
                    decision=critic.decision,
                    created_at=critic.created_at,
                ),
            )

        final_status = "approved" if overall_ok else "rejected"
        return QualityGateResponse(
            generation_id=generation.id,
            status="review",
            auto_checks_passed=overall_ok,
            manual_review_required=True,
            final_status=final_status,
            checks=[
                QualityCheckResponse(
                    id=UUID(int=0),
                    generation_id=generation.id,
                    asset_id=UUID(asset_id),
                    status="passed" if chk["passed"] else "failed",
                    checks=chk,
                    passed=chk["passed"],
                    created_at=datetime.now(UTC),
                )
                for asset_id, chk in checks.items()
            ],
            critic=VideoCriticResponse(
                id=critic.id,
                generation_id=critic.generation_id,
                identity_score=critic.identity_score,
                motion_score=critic.motion_score,
                prompt_adherence=critic.prompt_adherence,
                face_quality=critic.face_quality,
                artifact_score=critic.artifact_score,
                overall=critic.overall,
                decision=critic.decision,
                created_at=critic.created_at,
            ),
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
            "reviewed_at": datetime.now(UTC).isoformat(),
            "internal": False,
        }
        await self.repo.update_generation_status(generation.id, final_status, output_json=output)
        return ManualReviewResponse(
            id=UUID(int=0),
            generation_id=generation_id,
            status=final_status,
            passed=body.passed,
            review_comment=body.comment,
            reviewed_at=datetime.now(UTC),
        )

    async def _check_asset(self, asset_id: UUID, generation: Generation) -> dict:
        checks: dict[str, dict] = {}
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
        checks["audio"] = {"passed": bool(audio_ok), "value": bool(audio_ok)}
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

        checks["face_count"] = self._check_face_count(generation.output_json)
        if not checks["face_count"]["passed"]:
            passed = False

        checks["semantic"] = self._check_semantic(generation.output_json)
        if not checks["semantic"]["passed"]:
            passed = False

        checks["face_landmarks"] = self._check_face_landmarks(generation.output_json)
        if not checks["face_landmarks"]["passed"]:
            passed = False

        checks["blink"] = self._check_blink(generation.output_json)
        if not checks["blink"]["passed"]:
            passed = False

        return {"passed": passed, "checks": checks}

    async def _store_checks(self, generation_id: UUID, checks: dict, critic: VideoCriticResult) -> None:
        flatten: list[QualityCheck] = []
        for asset_id, chk in checks.items():
            if not isinstance(chk, dict):
                continue
            for check_type, detail in chk.get("checks", {}).items():
                value = detail.get("value")
                score = None
                if isinstance(value, (int, float)):
                    score = float(value)
                flatten.append(
                    QualityCheck(
                        generation_id=generation_id,
                        step_id=None,
                        check_type=check_type,
                        status="passed" if detail.get("passed") else "failed",
                        score=score,
                        details=detail,
                    )
                )
        if critic:
            flatten.append(
                QualityCheck(
                    generation_id=generation_id,
                    step_id=None,
                    check_type="video_critic",
                    status="passed" if critic.decision == "PASS" else "failed",
                    score=critic.overall,
                    details=critic.raw_response,
                )
            )
        self.db.add_all(flatten)
        await self.db.flush()

    def _check_face_count(self, output: dict) -> dict:
        expected = int((output.get("source_face") or {}).get("face_count") or 1)
        actual = int(output.get("face_count") or expected)
        ok = actual == expected
        return {
            "passed": ok,
            "expected": expected,
            "actual": actual,
        }

    def _check_semantic(self, output: dict) -> dict:
        expected = (output.get("prompt") or "").strip()
        detected = (output.get("scene_description") or "").strip()
        if not expected:
            return {"passed": True, "reason": "empty prompt"}
        ok = expected.lower() in detected.lower() or len(detected) > 0
        return {
            "passed": ok,
            "expected": expected,
            "detected": detected,
        }

    def _check_face_landmarks(self, output: dict) -> dict:
        metrics = output.get("face_metrics") or {}
        ok = metrics.get("landmarks_stable") is True or metrics.get("identity_score", 0) >= 0.8
        return {
            "passed": ok,
            "landmarks_stable": metrics.get("landmarks_stable"),
            "identity_score": metrics.get("identity_score"),
        }

    def _check_blink(self, output: dict) -> dict:
        metrics = output.get("face_metrics") or {}
        blink = metrics.get("blink_detected")
        ok = blink is not False
        return {
            "passed": ok,
            "blink_detected": blink,
        }
