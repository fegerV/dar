"""API dependencies for v1 endpoints."""

from fastapi import Depends

from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.models.admin import AdminUser


def require_admin(current_user=Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise ForbiddenException("Admin access required")
    return current_user


async def get_current_admin(
    current_user: AdminUser = Depends(require_admin),
) -> AdminUser:
    return current_user
