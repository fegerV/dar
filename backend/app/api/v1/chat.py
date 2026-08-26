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

_conversation_state: dict[str, dict] = {}


def _generate_response(user_id: str, text: str, project_id: str | None) -> tuple[str, list[str], str]:
    lower = text.lower().strip()

    state = _conversation_state.get(user_id, {"step": "start", "recipient": None, "occasion": None})

    if lower in ["начать", "привет", "привет!", "хай", "здравствуй"]:
        state["step"] = "start"
        _conversation_state[user_id] = state
        return (
            "Привет! Я Дарагент 🦊\n\n"
            "Я помогу создать персональное видеопоздравление, которое запомнится надолго!\n\n"
            "Кого сегодня поздравляем?",
            ["Маму ❤️", "Папу 💙", "Друга 🤝", "Коллегу 👔", "Вторую половинку 💕"],
            project_id or str(uuid4()),
        )

    if state["step"] == "start":
        recipient = text
        state["recipient"] = recipient
        state["step"] = "occasion"
        _conversation_state[user_id] = state

        if any(w in lower for w in ["мам", "маму", "маме"]):
            return (
                f"Мама ❤️ — это всегда особенный повод!\n\n"
                f"Какой у неё праздник?",
                ["День рождения 🎂", "Юбилей 🎉", "8 Марта 🌸", "Просто так 💝"],
                project_id or str(uuid4()),
            )
        elif any(w in lower for w in ["пап", "папу", "папе"]):
            return (
                f"Папа 💙 — нужно что-то мужское и запоминающееся!\n\n"
                f"Что празднуем?",
                ["День рождения 🎂", "Юбилей 🎉", "23 Февраля 🎖️", "Без повода"],
                project_id or str(uuid4()),
            )
        elif any(w in lower for w in ["друг", "друга", "подруга", "подругу"]):
            return (
                f"Друг 🤝 — давай придумаем что-то классное!\n\n"
                f"Какой повод?",
                ["День рождения 🎂", "Выпускной 🎓", "Свадьба 💒", "Без повода 🎉"],
                project_id or str(uuid4()),
            )
        elif any(w in lower for w in ["жен", "жену", "любимая", "девушк"]):
            return (
                f"Любимая 💕 — романтично!\n\n"
                f"Что планируем?",
                ["День рождения 🎂", "Годовщина 💍", "День Валентинка 💌", "Просто так 💝"],
                project_id or str(uuid4()),
            )
        elif any(w in lower for w in ["коллег", "коллега", "начальн", "босс"]):
            return (
                f"Коллега 👔 — держим формальтон!\n\n"
                f"Какой повод?",
                ["День рождения 🎂", "Профессиональный праздник 🏆", "Выпуск на пенсию 🎖️"],
                project_id or str(uuid4()),
            )
        else:
            return (
                f"{text} — отлично!\n\n"
                f"Какой у него/неё праздник?",
                ["День рождения 🎂", "Юбилей 🎉", "Свадьба 💒", "Без повода 🎉"],
                project_id or str(uuid4()),
            )

    if state["step"] == "occasion":
        occasion = text
        state["occasion"] = occasion
        state["step"] = "mood"
        _conversation_state[user_id] = state
        return (
            f"Отлично! {occasion} — это замечательный повод! 🎉\n\n"
            f"Какое настроение должно быть у поздравления?",
            ["Тёплое и душевное 🥹", "Весёлое и смешное 😂", "Эпичное и крутое 🚀", "Романтичное 💕"],
            project_id or str(uuid4()),
        )

    if state["step"] == "mood":
        mood = text
        state["mood"] = mood
        state["step"] = "photo"
        _conversation_state[user_id] = state
        return (
            f"Понял! {mood} — будет незабываемо! ✨\n\n"
            f"Теперь загрузи фото человека, которого поздравляем.\n"
            f"Это нужно, чтобы я мог создать персональное видео с его участием.",
            ["Загрузить фото 📸", "Пропустить этот шаг"],
            project_id or str(uuid4()),
        )

    if state["step"] == "photo":
        state["step"] = "confirm"
        _conversation_state[user_id] = state
        return (
            f"Фото получено! 📸\n\n"
            f"Давай подведём итоги:\n"
            f"• Получатель: {state.get('recipient', '—')}\n"
            f"• Повод: {state.get('occasion', '—')}\n"
            f"• Настроение: {state.get('mood', '—')}\n\n"
            f"Всё верно? Можешь начать генерацию!",
            ["Всё верно, начинать! 🚀", "Хочу изменить"],
            project_id or str(uuid4()),
        )

    if state["step"] == "confirm":
        state["step"] = "generating"
        _conversation_state[user_id] = state
        return (
            f"Отлично! Запускаю генерацию видеопоздравления 🎬\n\n"
            f"Это займёт около 2-5 минут. Я пришлю уведомление, когда будет готово!",
            ["Следить за прогрессом 📊"],
            project_id or str(uuid4()),
        )

    if lower in ["сброс", "заново", "начать заново", "reset"]:
        state = {"step": "start", "recipient": None, "occasion": None}
        _conversation_state[user_id] = state
        return (
            "Хорошо, начнём заново! 🔄\n\n"
            "Кого поздравляем?",
            ["Маму ❤️", "Папу 💙", "Друга 🤝", "Коллегу 👔", "Вторую половинку 💕"],
            project_id or str(uuid4()),
        )

    return (
        f"Интересно! 😊\n\n"
        f"Мы уже почти закончили. Хочешь начать генерацию или изменить что-то?",
        ["Начать генерацию 🚀", "Начать заново 🔄"],
        project_id or str(uuid4()),
    )


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    body: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = str(current_user.id)
    response_text, suggestions, project_id = _generate_response(user_id, body.text, body.project_id)

    message_id = str(uuid4())

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
