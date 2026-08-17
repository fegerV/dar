import os
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user

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
    return {
        "telegram_id": body.telegram_id,
        "username": body.username,
        "status": "linked",
    }


@router.post("/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    return {"ok": True, "update_id": payload.get("update_id")}
