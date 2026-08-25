from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ProjectCreateRequest,
    ProjectResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


def _generate_response(text: str) -> tuple[str, list[str]]:
    lower = text.lower()

    if any(w in lower for w in ["мам", "маму", "маме"]):
        return (
            "Мама ❤️ Расскажи мне о ней поближе.\n\nКакой у неё праздник?",
            ["День рождения", "Юбилей", "8 Марта", "Просто так"],
        )
    elif any(w in lower for w in ["пап", "папу", "папе"]):
        return (
            "Папа 💙 Какой у него праздник?",
            ["День рождения", "Юбилей", "23 Февраля"],
        )
    elif any(w in lower for w in ["друг", "друга"]):
        return (
            "Друг 🤝 Давай придумаем что-то классное!",
            ["День рождения", "Выпускной", "Без повода"],
        )
    elif any(w in lower for w in ["жен", "жену", "любимая"]):
        return (
            "Любимая 💕 Романтично! Что планируем?",
            ["День рождения", "Годовщина", "Валентинки"],
        )
    elif any(w in lower for w in ["коллег", "коллега", "начальн"]):
        return (
            "Коллега 👔 Держим формальтон!",
            ["День рождения", "Профессиональный праздник"],
        )
    else:
        return (
            f"Интересно! 😊 Расскажи подробнее о человеке, которого хочешь поздравить.",
            ["Это моя мама", "Это друг", "Это коллега"],
        )


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    body: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    response_text, suggestions = _generate_response(body.text)

    message_id = str(uuid4())
    project_id = body.project_id or str(uuid4())

    return ChatMessageResponse(
        id=message_id,
        project_id=project_id,
        text=response_text,
        sender="daragent",
        suggestions=suggestions,
        created_at=datetime.now(timezone.utc),
    )


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project_id = str(uuid4())

    return ProjectResponse(
        id=project_id,
        status="draft",
        recipient_name=body.recipient_name,
        occasion=body.occasion,
        mood=body.mood,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return ProjectResponse(
        id=str(project_id),
        status="draft",
        recipient_name="Елена",
        occasion="День рождения",
        created_at=datetime.now(timezone.utc),
    )
