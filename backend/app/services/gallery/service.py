from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.models.gallery import GalleryStatus, GallerySubmission
from app.models.generation import Generation
from app.repositories.gallery import GalleryRepository
from app.schemas.gallery import (
    GallerySubmissionCreate,
    GallerySubmissionResponse,
)


class GalleryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = GalleryRepository(db)

    async def submit(
        self, user_id: UUID, body: GallerySubmissionCreate
    ) -> GallerySubmissionResponse:
        if not body.consent_given:
            raise ValidationException("Требится согласие на публикацию в галерее")

        generation = await self.db.get(Generation, body.generation_id)
        if generation is None:
            raise NotFoundException("Видео не найдено")

        if generation.user_id != user_id:
            raise ForbiddenException("Нет доступа к этому видео")

        if generation.status != "completed":
            raise ValidationException("Только завершенные видео могут быть добавлены в галерею")

        output = generation.output_json or {}

        submission = GallerySubmission(
            generation_id=body.generation_id,
            user_id=user_id,
            project_id=generation.project_id,
            title=body.title,
            description=body.description,
            thumbnail_url=output.get("thumbnail_url"),
            video_url=output.get("video_url"),
            status=GalleryStatus.pending,
            is_public=False,
            consent_given=True,
        )
        submission = await self.repo.create(submission)
        await self.db.commit()
        return GallerySubmissionResponse.model_validate(submission)

    async def list_pending(self) -> list[GallerySubmissionResponse]:
        items = await self.repo.list_pending()
        return [GallerySubmissionResponse.model_validate(i) for i in items]

    async def review(
        self, submission_id: UUID, moderator_id: UUID, approve: bool, make_public: bool = False
    ) -> GallerySubmissionResponse:
        submission = await self.repo.get_by_id(submission_id)
        if submission is None:
            raise NotFoundException("Подача не найдена")

        status = GalleryStatus.approved if approve else GalleryStatus.rejected
        submission = await self.repo.update_status(
            submission_id,
            status,
            moderator_id=moderator_id,
            is_public=make_public if approve else False,
        )
        await self.db.commit()
        return GallerySubmissionResponse.model_validate(submission)

    async def list_public(self) -> list[GallerySubmissionResponse]:
        items = await self.repo.list_approved_public()
        return [GallerySubmissionResponse.model_validate(i) for i in items]

    async def list_my_submissions(self, user_id: UUID) -> list[GallerySubmissionResponse]:
        items = await self.repo.list_by_user(user_id)
        return [GallerySubmissionResponse.model_validate(i) for i in items]
