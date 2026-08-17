from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.brief import CreativeBrief
from app.models.project import Project
from app.models.recommendation import Recommendation
from app.repositories.projects import ProjectRepository
from app.repositories.recommendations import RecommendationRepository, TemplateRepository
from app.repositories.recipients import RecipientRepository
from app.schemas.recommendation import (
    RecommendationListResponse,
    RecommendationResponse,
    RecommendationSelectResponse,
)


class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RecommendationRepository(db)
        self.template_repo = TemplateRepository(db)
        self.project_repo = ProjectRepository(db)
        self.recipient_repo = RecipientRepository(db)

    async def generate(self, project_id: UUID) -> RecommendationListResponse:
        project = await self.project_repo.get_by_id(project_id, project_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)
        if brief is None:
            raise NotFoundException("Бриф не найден")

        recipient = await self.recipient_repo.get_by_id(project.recipient_id, project.owner_user_id)
        if recipient is None:
            raise NotFoundException("Получатель не найден")

        templates, _ = await self.template_repo.list_active(
            occasion_codes=[project.occasion_code] if project.occasion_code else None,
            relationship_types=[brief.relationship] if brief.relationship else None,
            moods=[brief.desired_mood] if brief.desired_mood else None,
            page_size=100,
        )

        scored = []
        for template in templates:
            score, reasons = self._score_template(template, brief, recipient, project.occasion_code)
            scored.append((template, score, reasons))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:5]

        recommendations = []
        for rank, (template, score, reasons) in enumerate(top, start=1):
            version = await self.template_repo.get_latest_version(template.id)
            rec = Recommendation(
                project_id=project_id,
                template_version_id=version.id if version else template.id,
                rank=rank,
                score=score,
                match_reasons=reasons,
                explanation=f"Шаблон '{template.title}' хорошо соответствует запросу",
                generated_by_model="rule_based_v1",
            )
            await self.repo.create(rec)
            recommendations.append(rec)

        await self.db.commit()
        return RecommendationListResponse(items=recommendations)

    async def list(self, project_id: UUID) -> RecommendationListResponse:
        items = await self.repo.list_by_project(project_id)
        return RecommendationListResponse(items=items)

    async def select(
        self, project_id: UUID, recommendation_id: UUID
    ) -> RecommendationSelectResponse:
        rec = await self.repo.get_by_id(recommendation_id, project_id)
        if rec is None:
            raise NotFoundException("Рекомендация не найдена")

        rec = await self.repo.mark_selected(recommendation_id, project_id, rec.template_version_id)
        if rec is None:
            raise NotFoundException("Рекомендация не найдена")

        project = await self.project_repo.get_by_id(project_id, project.owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        project.selected_recommendation_id = recommendation_id
        project.selected_template_version_id = rec.template_version_id
        project.status = "template_selected"
        project.updated_at = datetime.now(timezone.utc)
        await self.project_repo.update(project)
        await self.db.commit()

        return RecommendationSelectResponse(
            id=project.id,
            project_id=project_id,
            selected_template_version_id=rec.template_version_id,
            status=project.status,
        )

    def _score_template(
        self, template, brief: CreativeBrief, recipient, occasion_code: str | None
    ) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []

        if occasion_code and template.occasion_codes and occasion_code in template.occasion_codes:
            score += 0.25
            reasons.append("Подходит по поводу")

        if template.relationship_types and brief.relationship in template.relationship_types:
            score += 0.20
            reasons.append("Подходит по типу отношений")

        if template.moods and brief.desired_mood in template.moods:
            score += 0.20
            reasons.append("Подходит по настроению")

        if recipient.interests and template.metadata.get("interests"):
            intersection = set(recipient.interests) & set(template.metadata.get("interests", []))
            if intersection:
                score += 0.15
                reasons.append(f"Совпадение интересов: {', '.join(intersection)}")

        if brief.inside_joke and template.metadata.get("supports_inside_joke"):
            score += 0.05
            reasons.append("Поддерживает персональную шутку")

        if brief.hobbies_text and template.metadata.get("supports_hobbies"):
            score += 0.05
            reasons.append("Учитывает увлечения")

        if brief.sender_message and template.metadata.get("supports_sender_message"):
            score += 0.05
            reasons.append("Поддерживает сообщение отправителя")

        if brief.memorable_story and template.metadata.get("supports_stories"):
            score += 0.05
            reasons.append("Поддерживает истории")

        return min(score, 1.0), reasons
