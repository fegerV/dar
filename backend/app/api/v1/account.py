from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.users import UserRepository
from app.services.audit.service import AuditService

router = APIRouter(prefix="/account", tags=["Account"])


@router.delete("/me", status_code=204)
async def delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    from datetime import datetime, timezone
    user.deleted_at = datetime.now(timezone.utc)
    user.email = None
    user.phone = None
    user.display_name = None
    user.first_name = None
    user.last_name = None
    user.avatar_asset_id = None
    user.metadata = {}
    await db.flush()

    audit = AuditService(db)
    await audit.log(
        actor_user_id=current_user.id,
        action="account_deletion",
        target_type="user",
        target_id=current_user.id,
        metadata={"reason": "user_requested"},
    )
    await db.commit()
    return None
