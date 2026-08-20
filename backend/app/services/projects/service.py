from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.brief import CreativeBrief
from app.models.project import Project
from app.repositories.projects import ProjectRepository
from app.repositories.recipients import RecipientRepository
from app.schemas.brief import (
    BriefCompleteResponse,
    BriefQuestion,
    BriefQuestionOption,
    BriefQuestionsResponse,
    BriefSummaryResponse,
    BriefUpdate,
)
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

BRIEF_TRANSITIONS = {
    "draft": {"draft", "in_progress"},
    "in_progress": {"draft", "in_progress", "completed"},
    "completed": {"completed"},
}

REQUIRED_FIELDS_FOR_COMPLETION = [
    "relationship_",
    "desired_mood",
]


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.recipient_repo = RecipientRepository(db)

    async def create(self, owner_user_id: UUID, body: ProjectCreate) -> ProjectResponse:
        recipient = await self.recipient_repo.get_by_id(body.recipient_id, owner_user_id)
        if recipient is None:
            raise NotFoundException("Получатель не найден")

        project = Project(
            owner_user_id=owner_user_id,
            **body.model_dump(),
        )
        project = await self.project_repo.create(project)
        await self.db.flush()
        return ProjectResponse.model_validate(project)

    async def get(self, owner_user_id: UUID, project_id: UUID) -> ProjectResponse:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")
        return ProjectResponse.model_validate(project)

    async def list(
        self,
        owner_user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[ProjectResponse], int]:
        projects, total = await self.project_repo.list_by_owner(
            owner_user_id, page, page_size, status
        )
        return [ProjectResponse.model_validate(p) for p in projects], total

    async def update(
        self, owner_user_id: UUID, project_id: UUID, body: ProjectUpdate
    ) -> ProjectResponse:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)

        project.updated_at = datetime.now(UTC)
        await self.project_repo.update(project)
        await self.db.flush()
        return ProjectResponse.model_validate(project)

    async def get_brief(self, owner_user_id: UUID, project_id: UUID) -> BriefUpdate:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)
        if brief is None:
            return BriefUpdate()
        return BriefUpdate.model_validate(brief)

    async def save_brief(
        self, owner_user_id: UUID, project_id: UUID, body: BriefUpdate
    ) -> BriefUpdate:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)
        if brief is None:
            brief = CreativeBrief(project_id=project_id, status="draft")
            brief = await self.project_repo.create_brief(brief)

        transition_to = body.status
        if transition_to is not None:
            allowed = BRIEF_TRANSITIONS.get(brief.status, set())
            if transition_to not in allowed:
                raise ConflictException(
                    f"Cannot transition brief from '{brief.status}' to '{transition_to}'"
                )
            brief.status = transition_to

        update_data = body.model_dump(exclude_unset=True, exclude={"status"})
        for key, value in update_data.items():
            setattr(brief, key, value)

        brief.updated_at = datetime.now(UTC)
        brief.last_autosave_at = datetime.now(UTC)
        await self.project_repo.update_brief(brief)
        await self.db.flush()
        return BriefUpdate.model_validate(brief)

    async def complete_brief(
        self, owner_user_id: UUID, project_id: UUID
    ) -> BriefCompleteResponse:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)
        if brief is None:
            raise NotFoundException("Бриф не найден")

        allowed = BRIEF_TRANSITIONS.get(brief.status, set())
        if "completed" not in allowed:
            raise ConflictException(
                f"Cannot complete brief from status '{brief.status}'"
            )

        missing = [
            field for field in REQUIRED_FIELDS_FOR_COMPLETION
            if not getattr(brief, field, None)
        ]
        if missing:
            raise ValidationException(
                "Brief is missing required fields for completion",
                details={"missing_fields": missing},
            )

        brief.status = "completed"
        brief.completed_at = datetime.now(UTC)
        project.status = "recommendations_ready"
        project.updated_at = datetime.now(UTC)

        await self.project_repo.update_brief(brief)
        await self.project_repo.update(project)
        await self.db.flush()

        return BriefCompleteResponse(project_id=project_id, status=project.status)

    async def get_brief_summary(
        self, owner_user_id: UUID, project_id: UUID
    ) -> BriefSummaryResponse:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)
        if brief is None:
            brief = CreativeBrief(project_id=project_id, status="draft")
            brief = await self.project_repo.create_brief(brief)
            await self.db.flush()

        recipient_name = None
        if project.recipient_id:
            recipient = await self.recipient_repo.get_by_id(
                project.recipient_id, owner_user_id
            )
            if recipient:
                recipient_name = f"{recipient.first_name} {recipient.last_name or ''}".strip()

        filled_count = 0
        total_fields = 0
        brief_fields = [
            "occasion_text", "sender_role", "recipient_role",
            "relationship_text", "desired_mood", "inside_joke",
            "hobbies_text", "character_traits", "memorable_story",
            "desired_phrase", "forbidden_topics", "sender_message",
        ]
        for field_name in brief_fields:
            total_fields += 1
            if getattr(brief, field_name, None):
                filled_count += 1

        levels_filled = 0
        total_levels = 5
        for level_name in [
            "humor_level", "emotion_level", "surprise_level", "personalization_level"
        ]:
            if getattr(brief, level_name, None) is not None:
                levels_filled += 1

        completion_pct = 0
        if total_fields > 0:
            text_completion = filled_count / total_fields
            level_completion = levels_filled / total_levels
            completion_pct = round((text_completion * 0.6 + level_completion * 0.4) * 100)

        return BriefSummaryResponse(
            project_id=project_id,
            brief_status=brief.status,
            project_status=project.status,
            recipient_name=recipient_name,
            occasion=project.occasion_title or project.occasion_code,
            relationship=brief.relationship_text,
            desired_mood=brief.desired_mood,
            filled_fields=filled_count,
            total_fields=total_fields + total_levels,
            completion_percent=completion_pct,
            personalization_answers_count=len(brief.personalization_answers or {}),
            completed_at=brief.completed_at,
        )

    _MOOD_OPTIONS = [
        ("touching", "До слёз"),
        ("funny", "До смеха"),
        ("wow", "Вау!"),
        ("stylish", "Стильно"),
        ("cinematic", "Как кино"),
        ("unusual", "Необычно"),
    ]

    _RELATIONSHIP_QUESTIONS: dict[str, list[BriefQuestion]] = {
        "parent": [
            BriefQuestion(
                field="sender_role",
                label="Кто вы по отношению к получателю?",
                type="select",
                required=True,
                options=[
                    BriefQuestionOption(value="mother", label="Мама"),
                    BriefQuestionOption(value="father", label="Папа"),
                    BriefQuestionOption(value="son", label="Сын"),
                    BriefQuestionOption(value="daughter", label="Дочь"),
                ],
            ),
        ],
        "friend": [
            BriefQuestion(
                field="sender_role",
                label="Кто вы по отношению к получателю?",
                type="select",
                required=True,
                options=[
                    BriefQuestionOption(value="friend", label="Друг"),
                    BriefQuestionOption(value="close_friend", label="Близкий друг"),
                ],
            ),
        ],
        "colleague": [
            BriefQuestion(
                field="sender_role",
                label="Кто вы по отношению к получателю?",
                type="select",
                required=True,
                options=[
                    BriefQuestionOption(value="colleague", label="Коллега"),
                    BriefQuestionOption(value="boss", label="Начальник"),
                ],
            ),
        ],
    }

    _OCCASION_QUESTIONS: dict[str, list[BriefQuestion]] = {
        "birthday": [
            BriefQuestion(
                field="inside_joke",
                label="Есть ли личная шутка или воспоминание?",
                type="text",
                required=False,
                description="Добавьте персональный штрих к поздравлению",
            ),
        ],
        "new_year": [
            BriefQuestion(
                field="memorable_story",
                label="Вспомните знаковое событие этого года",
                type="text",
                required=False,
                description="Например: 'первый совместный поход в горы'",
            ),
        ],
        "wedding": [
            BriefQuestion(
                field="inside_joke",
                label="Свадьба — не без смешного! Добавьте личную шутку?",
                type="text",
                required=False,
            ),
        ],
    }

    async def get_brief_questions(
        self,
        owner_user_id: UUID,
        project_id: UUID,
        relationship: str | None,
        occasion_code: str | None,
    ) -> BriefQuestionsResponse:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)

        questions: list[BriefQuestion] = []

        rel_type = relationship or (brief.relationship_ if brief else None)
        rel_questions = self._RELATIONSHIP_QUESTIONS.get(rel_type, [])
        questions.extend(rel_questions)

        occ_code = occasion_code or project.occasion_code
        occ_questions = self._OCCASION_QUESTIONS.get(occ_code, [])
        questions.extend(occ_questions)

        base_questions = [
            BriefQuestion(
                field="relationship_text",
                label="Опишите отношения в свободном формате",
                type="text",
                required=True,
            ),
            BriefQuestion(
                field="desired_mood",
                label="Какое настроение вы хотите?",
                type="select",
                required=True,
                options=[
                    BriefQuestionOption(value=v, label=label)
                    for v, label in self._MOOD_OPTIONS
                ],
            ),
            BriefQuestion(
                field="inside_joke",
                label="Личная шутка (опционально)",
                type="text",
                required=False,
                description="Добавьте персональный штрих",
            ),
            BriefQuestion(
                field="sender_message",
                label="Ваше личное послание",
                type="textarea",
                required=True,
                description="Что вы хотите сказать получателю?",
            ),
            BriefQuestion(
                field="hobbies_text",
                label="Увлечения и хобби",
                type="text",
                required=False,
            ),
        ]
        questions.extend(base_questions)

        return BriefQuestionsResponse(
            project_id=project_id,
            relationship_type=rel_type,
            occasion_code=occ_code,
            questions=questions,
        )
