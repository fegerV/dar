from datetime import timedelta, datetime, timezone
import csv
import io
import logging
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.generation import Generation
from app.models.payment import Payment, Wallet
from app.models.project import Project
from app.models.user import User

logger = logging.getLogger(__name__)


class AccountDeletionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_user_data(self, user_id: UUID) -> dict:
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user is None:
            return {}

        export_data = {
            "user": {
                "id": str(user.id),
                "display_name": user.display_name,
                "email": user.email,
                "phone": user.phone,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "locale": user.locale,
                "timezone": user.timezone,
                "currency": user.currency,
                "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_seen_at": user.last_seen_at.isoformat() if user.last_seen_at else None,
            },
        }

        wallet_result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = wallet_result.scalar_one_or_none()
        if wallet:
            export_data["wallet"] = {
                "balance_rub": str(wallet.balance_rub),
                "bonus_balance": str(wallet.bonus_balance),
                "updated_at": wallet.updated_at.isoformat() if wallet.updated_at else None,
            }

        payment_result = await self.db.execute(
            select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at)
        )
        export_data["payments"] = [
            {
                "id": str(p.id),
                "amount_rub": str(p.amount_rub),
                "status": p.status,
                "method": p.method,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "paid_at": p.paid_at.isoformat() if p.paid_at else None,
            }
            for p in payment_result.scalars().all()
        ]

        project_result = await self.db.execute(
            select(Project).where(Project.owner_user_id == user_id)
        )
        projects = project_result.scalars().all()
        export_data["projects"] = [
            {
                "id": str(p.id),
                "title": p.title,
                "status": p.status,
                "occasion_code": p.occasion_code,
                "occasion_title": p.occasion_title,
                "price_rub": str(p.price_rub),
                "paid_rub": str(p.paid_rub),
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "completed_at": p.completed_at.isoformat() if p.completed_at else None,
            }
            for p in projects
        ]

        generation_result = await self.db.execute(
            select(Generation).where(
                Generation.project_id.in_(select(Project.id).where(Project.owner_user_id == user_id))
            )
        )
        export_data["generations"] = [
            {
                "id": str(g.id),
                "project_id": str(g.project_id),
                "type": g.type,
                "status": g.status,
                "created_at": g.created_at.isoformat() if g.created_at else None,
                "started_at": g.started_at.isoformat() if g.started_at else None,
                "completed_at": g.completed_at.isoformat() if g.completed_at else None,
            }
            for g in generation_result.scalars().all()
        ]

        audit_result = await self.db.execute(
            select(AuditLog).where(AuditLog.actor_user_id == user_id)
        )
        export_data["audit_logs"] = [
            {
                "action": log.action,
                "target_type": log.target_type,
                "target_id": str(log.target_id) if log.target_id else None,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in audit_result.scalars().all()
        ]

        return export_data

    async def get_data_csv(self, user_id: UUID, table_name: str) -> str:
        model_map = {
            "payments": Payment,
            "wallets": Wallet,
            "projects": Project,
            "generations": Generation,
        }
        model = model_map.get(table_name)
        if model is None:
            return ""

        if hasattr(model, "user_id"):
            fk_attr = "user_id"
        elif hasattr(model, "owner_user_id"):
            fk_attr = "owner_user_id"
        elif hasattr(model, "project_id"):
            return ""
        else:
            return ""

        result = await self.db.execute(
            select(model).where(getattr(model, fk_attr) == user_id)
        )
        rows = result.scalars().all()

        if not rows:
            return ""

        output = io.StringIO()
        writer = csv.writer(output)
        columns = [c for c in rows[0].__table__.columns.keys()]
        writer.writerow(columns)
        for row in rows:
            writer.writerow([
                str(getattr(row, c, "")) if getattr(row, c, None) is not None else ""
                for c in columns
            ])

        return output.getvalue()

    async def anonymize_user(self, user_id: UUID) -> None:
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user is None:
            return

        anon_prefix = f"deleted_{user_id.hex[:8]}_"
        user.email = None
        user.phone = None
        user.display_name = f"{anon_prefix}user"
        user.first_name = None
        user.last_name = None
        user.avatar_asset_id = None
        user.birth_date = None
        user.metadata_ = {}
        user.status = "deleted"
        user.deleted_at = datetime.now(timezone.utc)

        from app.services.audit.service import AuditService

        audit = AuditService(self.db)
        await audit.log(
            actor_user_id=user_id,
            action="account_anonymized",
            target_type="user",
            target_id=user_id,
            metadata={"method": "gdpr_anonymization"},
        )

        await self.db.commit()

    async def hard_delete_user(self, user_id: UUID, admin_override: bool = False) -> dict:
        from app.core.exceptions import ValidationException

        if not admin_override:
            raise ValidationException("Hard delete requires admin override")

        result = await self.db.execute(
            select(AuditLog).where(AuditLog.actor_user_id == user_id)
        )
        audit_count = len(result.scalars().all())

        from app.services.audit.service import AuditService

        audit = AuditService(self.db)
        await audit.log(
            actor_user_id=user_id,
            action="account_hard_delete",
            target_type="user",
            target_id=user_id,
            metadata={"audit_logs_found": audit_count},
        )

        await self.db.execute(delete(Payment).where(Payment.user_id == user_id))
        await self.db.execute(delete(Wallet).where(Wallet.user_id == user_id))
        await self.db.execute(delete(Project).where(Project.owner_user_id == user_id))
        await self.db.execute(delete(AuditLog).where(AuditLog.actor_user_id == user_id))
        await self.db.execute(delete(User).where(User.id == user_id))

        await self.db.commit()
        return {"deleted": True, "audit_log_count": audit_count}

    async def schedule_deletion(self, user_id: UUID) -> dict:
        from app.core.config import settings

        if settings.APP_ENV == "production":
            await self.anonymize_user(user_id)
            return {
                "deleted": False,
                "scheduled": True,
                "deletion_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                "message": "Data anonymized. Hard deletion scheduled after 30-day grace period.",
            }

        await self.anonymize_user(user_id)
        return {
            "deleted": True,
            "scheduled": False,
            "message": "Data anonymized (non-production environment).",
        }
