from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.template import Template, TemplateVersion
from app.models.user import User
from app.repositories.projects import ProjectRepository

VALID_TEMPLATE_STATUSES = {"draft", "testing", "published", "paused", "archived"}
VALID_VERSION_STATUSES = {"draft", "testing", "published", "paused", "archived"}
QA_REQUIRED_FIELDS = {
    "model_name",
    "prompt_config",
    "render_config",
    "negative_prompt",
    "max_duration_sec",
}
QA_CHECKLIST_ITEMS = [
    "face_quality_verified",
    "prompt_adherence_verified",
    "duration_valid",
    "style_consistency",
    "content_safety_reviewed",
    "audio_quality_test",
]


class TemplateVersionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)

    async def create_version(self, template_id: UUID, user_id: UUID, schema_version: str = "1.0") -> TemplateVersion:
        template = await self._get_template_if_admin(template_id, user_id)
        if template is None:
            raise NotFoundException("Template not found")

        latest_result = await self.db.execute(
            select(TemplateVersion)
            .where(TemplateVersion.template_id == template_id)
            .order_by(TemplateVersion.version.desc())
            .limit(1)
        )
        latest = latest_result.scalar_one_or_none()
        next_version = (latest.version + 1) if latest else 1

        version = TemplateVersion(
            template_id=template_id,
            version=next_version,
            status="draft",
            schema_version=schema_version,
            prompt_config={},
            render_config={},
            personalization_config={},
            validation_config={},
            qa_checklist={},
        )
        self.db.add(version)
        await self.db.flush()
        return version

    async def update_version(
        self,
        version_id: UUID,
        user_id: UUID,
        prompt_config: dict | None = None,
        render_config: dict | None = None,
        personalization_config: dict | None = None,
        validation_config: dict | None = None,
        max_duration_sec: int | None = None,
        qa_checklist: dict | None = None,
    ) -> TemplateVersion:
        version = await self._get_version_if_admin(version_id, user_id)
        if version is None:
            raise NotFoundException("Template version not found")

        if version.status not in ("draft", "testing"):
            raise ValidationException(
                f"Cannot update version in '{version.status}' status. Must be draft or testing."
            )

        if prompt_config is not None:
            version.prompt_config = prompt_config
        if render_config is not None:
            version.render_config = render_config
        if personalization_config is not None:
            version.personalization_config = personalization_config
        if validation_config is not None:
            version.validation_config = validation_config
        if max_duration_sec is not None:
            version.max_duration_sec = max_duration_sec
        if qa_checklist is not None:
            version.qa_checklist = qa_checklist

        await self.db.flush()
        return version

    async def transition_status(self, version_id: UUID, user_id: UUID, new_status: str) -> TemplateVersion:
        if new_status not in VALID_VERSION_STATUSES:
            raise ValidationException(f"Invalid status: {new_status}")

        version = await self._get_version_if_admin(version_id, user_id)
        if version is None:
            raise NotFoundException("Template version not found")

        current = version.status
        if current == new_status:
            return version

        errors = self._validate_transition(current, new_status, version)
        if errors:
            raise ValidationException(
                f"Cannot transition from '{current}' to '{new_status}': " + "; ".join(errors)
            )

        if new_status == "published":
            version.published_at = datetime.now(timezone.utc)
        if new_status == "archived":
            version.retired_at = datetime.now(timezone.utc)

        version.status = new_status
        await self.db.flush()
        return version

    def _validate_transition(self, current: str, target: str, version: TemplateVersion) -> list[str]:
        errors: list[str] = []

        can_publish = all(
            k in version.prompt_config and version.prompt_config[k] is not None
            for k in QA_REQUIRED_FIELDS
        ) or version.prompt_config

        if target == "published":
            if not can_publish:
                errors.append("prompt_config must be populated")
            if version.max_duration_sec is None:
                errors.append("max_duration_sec must be set")
            checklist = version.qa_checklist or {}
            missing_items = [item for item in QA_CHECKLIST_ITEMS if not checklist.get(item)]
            if missing_items:
                errors.append(f"QA checklist items missing: {', '.join(missing_items)}")
            if version.render_config is None and not isinstance(version.render_config, dict):
                errors.append("render_config must be valid")

        if target == "testing":
            if not can_publish:
                errors.append("prompt_config must be populated before testing")

        if current == "published" and target == "draft":
            errors.append("Cannot revert published version to draft")

        if current == "archived":
            errors.append("Cannot modify an archived version")

        return errors

    async def get_version(self, version_id: UUID, user_id: UUID | None = None) -> TemplateVersion | None:
        version = await self.db.get(TemplateVersion, version_id)
        if version is None:
            return None
        if user_id is not None:
            result = await self.db.execute(select(Template).where(Template.id == version.template_id))
            template = result.scalar_one_or_none()
            if template is None:
                return None
        return version

    async def list_versions(self, template_id: UUID, user_id: UUID | None = None, status: str | None = None) -> list[TemplateVersion]:
        query = select(TemplateVersion).where(TemplateVersion.template_id == template_id)
        if status:
            query = query.where(TemplateVersion.status == status)
        query = query.order_by(TemplateVersion.version.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _get_version_if_admin(self, version_id: UUID, user_id: UUID) -> TemplateVersion | None:
        version = await self.db.get(TemplateVersion, version_id)
        if version is None:
            return None

        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user and not user.is_admin:
            return None

        return version

    async def _get_template_if_admin(self, template_id: UUID, user_id: UUID) -> Template | None:
        template = await self.db.get(Template, template_id)
        if template is None:
            return None

        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user and not user.is_admin:
            return None

        return template
