from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
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

    async def get_upload_url(self, body: AssetUploadRequest, user_id: UUID) -> AssetUploadResponse:
        asset_id = UUID(int=0)  # placeholder, replace with real UUID generation
        # In real implementation, generate presigned MinIO/Yandex Disk URL
        upload_url = f"http://localhost:9000/daragent/upload/{asset_id}"
        return AssetUploadResponse(asset_id=asset_id, upload_url=upload_url, expires_in=900)

    async def list_assets(
        self, user_id: UUID, page: int = 1, page_size: int = 20
    ) -> AssetListResponse:
        # Stub implementation
        return AssetListResponse(items=[], total=0, page=page, page_size=page_size)

    async def confirm_upload(self, asset_id: UUID, user_id: UUID) -> AssetResponse:
        asset = await self.storage_repo.get_asset(asset_id)
        if asset is None:
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
