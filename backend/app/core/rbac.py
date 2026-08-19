"""RBAC: permission checking for admin endpoints."""
from __future__ import annotations

from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.models.admin import Role, UserRole
from app.models.user import User


SYSTEM_ROLES = {
    "owner": {
        "name": "Владелец",
        "description": "Full access to all features",
        "permissions": ["*"],
    },
    "admin": {
        "name": "Администратор",
        "description": "Almost full access",
        "permissions": [
            "users.*", "orders.*", "generations.*", "queue.*",
            "templates.*", "scenes.*", "prompts.*", "workflows.*",
            "models.*", "workers.*", "payments.*", "wallet.*",
            "promo.*", "moderation.*", "support.*", "analytics.*",
            "settings.*", "audit.*", "logs.*", "errors.*",
            "recommendations.*",
        ],
    },
    "content_manager": {
        "name": "Контент-менеджер",
        "description": "Контент: шаблоны, сцены, prompts",
        "permissions": ["templates.*", "scenes.*", "prompts.*"],
    },
    "ai_operator": {
        "name": "AI-оператор",
        "description": "AI, очередь, воркеры",
        "permissions": ["generations.*", "queue.*", "workers.*", "models.*"],
    },
    "support": {
        "name": "Поддержка",
        "description": "Пользователи, заказы, поддержка",
        "permissions": ["users.read", "orders.*", "support.*", "wallet.read"],
    },
    "moderator": {
        "name": "Модератор",
        "description": "Модерация контента",
        "permissions": ["moderation.*"],
    },
    "analyst": {
        "name": "Аналитик",
        "description": "Read-only access",
        "permissions": [
            "orders.read", "generations.read", "queue.read",
            "users.read", "payments.read", "analytics.*",
            "audit.read", "logs.read", "templates.read",
            "scenes.read", "prompts.read", "models.read",
            "workers.read", "wallet.read",
        ],
    },
}


def permission_allowed(user_permissions: list[str], required: str) -> bool:
    if "*" in user_permissions:
        return True
    if required in user_permissions:
        return True
    parts = required.split(".")
    for i in range(1, len(parts) + 1):
        wildcard = ".".join(parts[:i]) + ".*"
        if wildcard in user_permissions:
            return True
    return False


@lru_cache(maxsize=1)
def get_role_permissions(role_code: str) -> list[str]:
    return SYSTEM_ROLES.get(role_code, {}).get("permissions", [])


async def get_user_permissions(
    user: User,
    db: AsyncSession,
) -> list[str]:
    if user.is_admin:
        return ["*"]

    result = await db.execute(
        select(Role, UserRole)
        .join(UserRole, Role.id == UserRole.role_id)
        .where(UserRole.user_id == user.id)
        .where(Role.is_active if hasattr(Role, "is_active") else True)
    )
    permissions: list[str] = []
    for role, _ in result.all():
        permissions.extend(get_role_permissions(role.code))
        if role.permissions:
            permissions.extend(role.permissions)
    return permissions


def require_permission(permission: str):
    async def dependency(
        current_user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        perms = await get_user_permissions(current_user, db)
        if not permission_allowed(perms, permission):
            raise ForbiddenException(f"Missing permission: {permission}")
        return current_user
    return dependency
