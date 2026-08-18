import hashlib
import hmac
import json
from datetime import datetime, timezone
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundException, ValidationException
from app.models.payment import Payment, Wallet
from app.repositories.storage import PaymentRepository, WalletRepository
from app.schemas.payment import PaymentResponse, WalletResponse


class YooKassaClient:
    BASE_URL = "https://api.yookassa.ru/v3"

    def __init__(self):
        self.shop_id = settings.YOOKASSA_SHOP_ID
        self.secret_key = settings.YOOKASSA_SECRET_KEY
        self.webhook_secret = settings.YOOKASSA_WEBHOOK_SECRET
        self.return_url = settings.YOOKASSA_RETURN_URL

    async def create_payment(
        self,
        amount: float,
        currency: str = "RUB",
        description: str = "",
        idempotency_key: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        if not self.shop_id or not self.secret_key:
            return {
                "id": f"mock_{UUID(int=0).hex}",
                "status": "pending",
                "amount": {"value": f"{amount:.2f}", "currency": currency},
                "confirmation": {"confirmation_url": "http://localhost:8000/mock-payment"},
            }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.BASE_URL}/payments",
                auth=(self.shop_id, self.secret_key),
                headers={
                    "Content-Type": "application/json",
                    "Idempotence-Key": idempotency_key or f"payment_{datetime.now(timezone.utc).timestamp()}",
                },
                json={
                    "amount": {"value": f"{amount:.2f}", "currency": currency},
                    "description": description,
                    "confirmation": {"type": "redirect", "return_url": self.return_url},
                    "capture": True,
                    "metadata": metadata or {},
                },
            )
            data = response.json()
            if response.status_code >= 400:
                raise ValidationException(f"YooKassa error: {data}")
            return data

    async def get_payment(self, payment_id: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.BASE_URL}/payments/{payment_id}",
                auth=(self.shop_id, self.secret_key),
            )
            data = response.json()
            if response.status_code >= 400:
                raise ValidationException(f"YooKassa error: {data}")
            return data

    def verify_webhook_signature(self, body_bytes: bytes, signature: str | None) -> bool:
        if not self.webhook_secret:
            return False
        if not signature:
            return False
        expected = hmac.new(
            self.webhook_secret.encode(),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wallet_repo = WalletRepository(db)

    async def get_or_create_wallet(self, user_id: UUID) -> Wallet:
        wallet = await self.wallet_repo.get_by_user_id(user_id)
        if wallet is None:
            wallet = Wallet(user_id=user_id, balance_rub=0, bonus_balance=0)
            await self.wallet_repo.create(wallet)
            await self.db.commit()
        return wallet

    async def get_wallet(self, user_id: UUID) -> WalletResponse:
        wallet = await self.get_or_create_wallet(user_id)
        return WalletResponse.model_validate(wallet)

    async def credit(self, user_id: UUID, amount: float, bonus: bool = False) -> WalletResponse:
        wallet = await self.get_or_create_wallet(user_id)
        if bonus:
            wallet.bonus_balance = (wallet.bonus_balance or 0) + amount
        else:
            wallet.balance_rub = (wallet.balance_rub or 0) + amount
        wallet.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        return WalletResponse.model_validate(wallet)

    async def debit(self, user_id: UUID, amount: float) -> WalletResponse:
        wallet = await self.get_or_create_wallet(user_id)
        if (wallet.balance_rub or 0) < amount:
            raise ValidationException("Недостаточно средств на кошельке")
        wallet.balance_rub = (wallet.balance_rub or 0) - amount
        wallet.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        return WalletResponse.model_validate(wallet)


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.wallet_repo = WalletRepository(db)
        self.yookassa = YooKassaClient()
        self.wallet_service = WalletService(db)

    async def create_payment(
        self, user_id: UUID, project_id: UUID, amount: float, method: str = "bank_card"
    ) -> PaymentResponse:
        payment = Payment(
            user_id=user_id,
            project_id=project_id,
            provider_id=UUID(int=0),
            status="pending",
            method=method,
            amount_rub=amount,
            bonus_amount_rub=0,
            discount_rub=0,
            provider_payload={},
        )
        await self.payment_repo.create(payment)
        await self.db.commit()

        yookassa_payment = await self.yookassa.create_payment(
            amount=amount,
            description=f"Поздравление #{project_id}",
            idempotency_key=str(payment.id),
            metadata={"payment_id": str(payment.id), "project_id": str(project_id)},
        )

        payment.external_payment_id = yookassa_payment.get("id")
        payment.idempotency_key = str(payment.id)
        payment.provider_payload = yookassa_payment
        confirmation_url = yookassa_payment.get("confirmation", {}).get("confirmation_url")
        await self.db.commit()

        response = PaymentResponse.model_validate(payment)
        if confirmation_url:
            response.confirmation_url = confirmation_url
        return response

    async def handle_webhook(self, raw_body: bytes, body: dict, signature: str | None = None) -> dict:
        if not signature or not self.yookassa.verify_webhook_signature(
            raw_body, signature
        ):
            raise ValidationException("Invalid webhook signature")

        event = body.get("event")
        payment_id = body.get("object", {}).get("id")
        status = body.get("object", {}).get("status")

        payment = await self.payment_repo.get_by_id(UUID(body.get("metadata", {}).get("payment_id")))
        if payment is None and payment_id:
            from sqlalchemy import select
            result = await self.db.execute(
                select(Payment).where(Payment.external_payment_id == payment_id)
            )
            payment = result.scalar_one_or_none()

        if payment is None:
            return {"received": True, "status": "ignored"}

        payment.provider_payload = body
        paid_at = None

        if event == "payment.succeeded" or status == "succeeded":
            payment.status = "paid"
            paid_at = datetime.now(timezone.utc)
        elif event == "payment.canceled" or status == "canceled":
            payment.status = "failed"
        elif event == "payment.waiting_for_capture" or status == "waiting_for_capture":
            payment.status = "authorized"

        if paid_at:
            payment.paid_at = paid_at
            await self.wallet_service.credit(payment.user_id, payment.amount_rub)

        await self.db.commit()
        return {"received": True, "payment_id": str(payment.id), "status": payment.status}

    async def get_payment(self, payment_id: UUID, user_id: UUID | None = None) -> PaymentResponse:
        payment = await self.payment_repo.get_by_id(payment_id)
        if payment is None:
            raise NotFoundException("Платёж не найден")
        if user_id is not None and payment.user_id != user_id:
            raise NotFoundException("Платёж не найден")
        return PaymentResponse.model_validate(payment)
