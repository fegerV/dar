
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/telegram", tags=["Telegram"])


class TelegramLinkRequest(BaseModel):
    telegram_id: int
    username: str | None = None


@router.post("/link")
async def link_telegram(
    body: TelegramLinkRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = await db.get(User, current_user.id)
    if user is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("User not found")

    user.telegram_user_id = body.telegram_id
    if body.username:
        user.metadata_["telegram_username"] = body.username
    await db.commit()
    await db.refresh(user)
    return {
        "telegram_id": user.telegram_user_id,
        "username": user.metadata_.get("telegram_username"),
        "status": "linked",
    }


@router.post("/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    return {"ok": True, "update_id": payload.get("update_id")}
