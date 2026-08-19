from uuid import UUID

from app.core.exceptions import ValidationException
from app.models.intelligence import ImagePreflightResult
from app.repositories.generations import GenerationRepository


class ImagePreflightService:
    MIN_SHARPNESS = 0.7
    MIN_QUALITY = 70.0

    def __init__(self, db) -> None:
        self.db = db
        self.generation_repo = GenerationRepository(db)

    async def analyze(self, generation_id: UUID, image_url: str, image_metadata: dict | None = None, user_id: UUID | None = None) -> ImagePreflightResult:
        generation = await self.generation_repo.get_by_id(generation_id)
        if generation is None:
            raise ValidationException("Генерация не найдена")

        if user_id is not None:
            from app.repositories.projects import ProjectRepository

            project_repo = ProjectRepository(self.db)
            project = await project_repo.get_by_id(generation.project_id, user_id)
            if project is None:
                raise ValidationException("Генерация не найдена")

        metadata = image_metadata or {}
        quality_score = float(metadata.get("quality_score", 85))
        face_count = int(metadata.get("face_count", 1))
        face_size = str(metadata.get("face_size", "large"))
        pose = str(metadata.get("pose", "frontal"))
        sharpness = float(metadata.get("sharpness", 0.9))
        issues = metadata.get("issues", [])

        recommended_models = self._recommend_models(metadata)
        recommended_templates = self._recommend_templates(metadata)

        result = ImagePreflightResult(
            generation_id=generation.id,
            image_url=image_url,
            quality_score=quality_score,
            face_count=face_count,
            face_size=face_size,
            pose=pose,
            sharpness=sharpness,
            recommended_models=recommended_models,
            recommended_templates=recommended_templates,
            issues=list(issues),
            raw_response=metadata,
        )
        self.db.add(result)
        await self.db.flush()
        return result

    def _recommend_models(self, metadata: dict) -> list[str]:
        if metadata.get("face_count", 1) > 1:
            return ["kling", "veo"]
        if metadata.get("pose") == "profile":
            return ["veo", "kling"]
        return ["grok", "veo", "kling"]

    def _recommend_templates(self, metadata: dict) -> list[str]:
        templates = ["portrait_speech"]
        if metadata.get("pose") == "frontal" and metadata.get("face_size") == "large":
            templates.append("warm_smile")
        if metadata.get("sharpness", 0) >= 0.85:
            templates.append("cinematic_push_in")
        return templates

    def is_acceptable(self, result: ImagePreflightResult) -> bool:
        if result.quality_score is not None and result.quality_score < self.MIN_QUALITY:
            return False
        if result.sharpness is not None and result.sharpness < self.MIN_SHARPNESS:
            return False
        if result.face_count is not None and result.face_count != 1:
            return False
        if result.face_size == "small":
            return False
        return True
