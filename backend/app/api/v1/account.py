from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.repositories.users import UserRepository
from app.services.account.deletion import AccountDeletionService
from app.services.audit.service import AuditService

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/export", response_model=dict)
async def export_my_data(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AccountDeletionService(db)
    data = await service.export_user_data(current_user.id)
    audit = AuditService(db)
    await audit.log(
        actor_user_id=current_user.id,
        action="gdpr_data_export",
        target_type="user",
        target_id=current_user.id,
    )
    await db.commit()
    return data


@router.get("/export/{table_name}", response_class=__import__("fastapi").Response)
async def export_my_data_csv(
    table_name: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AccountDeletionService(db)
    csv_data = await service.get_data_csv(current_user.id, table_name)
    from fastapi.responses import PlainTextResponse

    return PlainTextResponse(content=csv_data, media_type="text/csv")


@router.post("/delete-request", response_model=dict)
async def request_account_deletion(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AccountDeletionService(db)
    result = await service.schedule_deletion(current_user.id)
    return result


@router.delete("/me", status_code=204)
async def delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.id)
    if not user:
        raise NotFoundException("User not found")

    user.deleted_at = datetime.now(UTC)
    user.email = None
    user.phone = None
    user.display_name = None
    user.first_name = None
    user.last_name = None
    user.avatar_asset_id = None
    user.metadata_ = {}
    await db.flush()

    audit = AuditService(db)
    await audit.log(
        actor_user_id=current_user.id,
        action="account_deletion",
        target_type="user",
        target_id=current_user.id,
        metadata={"reason": "user_requested", "method": "soft_delete"},
    )
    await db.commit()
    return None


@router.delete("/me/hard", response_model=dict)
async def hard_delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.core.exceptions import ForbiddenException

    if not getattr(current_user, "is_admin", False):
        raise ForbiddenException("Admin access required for hard deletion")

    service = AccountDeletionService(db)
    result = await service.hard_delete_user(current_user.id, admin_override=True)
    return result
