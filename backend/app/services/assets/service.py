from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.integrations.storage.factory import get_storage_provider
from app.models.asset import Asset, StorageObject
from app.models.payment import Payment
from app.repositories.storage import PaymentRepository, StorageRepository, WalletRepository
from app.schemas.asset import AssetUploadRequest, AssetUploadResponse, AssetResponse, AssetListResponse
from app.schemas.payment import (
    EntitlementResponse,
    PaymentCreate,
    PaymentResponse,
    PaymentWebhookResponse,
    WalletResponse,
)


class AssetService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage_repo = StorageRepository(db)
        self.storage = get_storage_provider()

    async def get_upload_url(self, body: AssetUploadRequest, user_id: UUID) -> AssetUploadResponse:
        import uuid
        asset_id = uuid.uuid4()
        object_key = f"uploads/{user_id}/{asset_id}_{body.filename}"
        upload_url = await self.storage.generate_presigned_upload_url(
            bucket="daragent",
            object_key=object_key,
            expires_in=900,
            content_type=body.mime_type,
        )
        return AssetUploadResponse(asset_id=asset_id, upload_url=upload_url, expires_in=900)

    async def confirm_upload(self, asset_id: UUID, user_id: UUID, object_key: str) -> AssetResponse:
        storage_obj = StorageObject(
            bucket="daragent",
            object_key=object_key,
            original_name=object_key.split("/")[-1],
        )
        storage_obj = await self.storage_repo.create_object(storage_obj)

        asset = Asset(
            owner_user_id=user_id,
            type="file",
            status="uploaded",
            storage_object_id=storage_obj.id,
        )
        asset = await self.storage_repo.create_asset(asset)
        await self.db.commit()
        return AssetResponse.model_validate(asset)

    async def list_assets(
        self, user_id: UUID, page: int = 1, page_size: int = 20
    ) -> AssetListResponse:
        from sqlalchemy import select, func
        from app.models.asset import Asset

        count_query = select(func.count()).select_from(Asset).where(Asset.owner_user_id == user_id)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = (
            select(Asset)
            .where(Asset.owner_user_id == user_id)
            .order_by(Asset.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        items = [AssetResponse.model_validate(a) for a in result.scalars().all()]
        return AssetListResponse(items=items, total=total, page=page, page_size=page_size)

    async def get_asset(self, asset_id: UUID, user_id: UUID) -> AssetResponse:
        asset = await self.storage_repo.get_asset(asset_id)
        if asset is None or asset.owner_user_id != user_id:
            raise NotFoundException("Asset not found")
        return AssetResponse.model_validate(asset)



class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wallet_repo = WalletRepository(db)

    async def get_or_create_wallet(self, user_id: UUID):
        from app.models.payment import Wallet
        wallet = await self.wallet_repo.get_by_user_id(user_id)
        if wallet is None:
            wallet = Wallet(user_id=user_id, balance_rub=0, bonus_balance=0)
            await self.wallet_repo.create(wallet)
            await self.db.commit()
        return wallet

    async def get_wallet(self, user_id: UUID) -> WalletResponse:
        wallet = await self.get_or_create_wallet(user_id)
        return WalletResponse.model_validate(wallet)


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.wallet_service = WalletService(db)

    async def create_payment(self, user_id: UUID, project_id: UUID, body: PaymentCreate) -> PaymentResponse:
        payment = Payment(
            user_id=user_id,
            project_id=project_id,
            method=body.method,
            amount_rub=0,  # calculated elsewhere
            bonus_amount_rub=0,
            discount_rub=0,
            status="pending",
        )
        await self.payment_repo.create(payment)
        await self.db.commit()
        return PaymentResponse.model_validate(payment)

    async def handle_webhook(self, body: PaymentWebhookRequest) -> PaymentWebhookResponse:
        # Idempotent webhook processing
        return PaymentWebhookResponse(received=True)
