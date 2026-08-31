from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, StorageObject


class StorageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_object(self, obj: StorageObject) -> StorageObject:
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def create_asset(self, asset: Asset) -> Asset:
        self.db.add(asset)
        await self.db.flush()
        return asset

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        result = await self.db.execute(select(Asset).where(Asset.id == asset_id))
        return result.scalar_one_or_none()


class WalletRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: UUID):
        from app.models.payment import Wallet
        result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, wallet) -> None:
        self.db.add(wallet)
        await self.db.flush()


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payment) -> None:
        self.db.add(payment)
        await self.db.flush()

    async def get_by_id(self, payment_id: UUID):
        from app.models.payment import Payment
        result = await self.db.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()
