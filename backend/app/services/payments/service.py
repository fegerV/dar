import hashlib
import hmac
import logging
import secrets
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.payment import Payment, PaymentIdempotencyKey, Wallet
from app.repositories.storage import PaymentRepository, WalletRepository
from app.schemas.payment import PaymentResponse, WalletResponse

logger = logging.getLogger(__name__)
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0


class IdempotencyService:
    """Service for handling idempotent payment operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create_idempotency_key(
        self, 
        user_id: UUID, 
        idempotency_key: str
    ) -> PaymentIdempotencyKey | None:
        """Get existing idempotency key or create new one."""
        result = await self.db.execute(
            select(PaymentIdempotencyKey).where(
                PaymentIdempotencyKey.idempotency_key == idempotency_key,
                PaymentIdempotencyKey.user_id == user_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        new_key = PaymentIdempotencyKey(
            user_id=user_id,
            idempotency_key=idempotency_key,
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(hours=24)
        )
        self.db.add(new_key)
        return new_key
    
    async def check_and_set_idempotency(
        self,
        user_id: UUID,
        idempotency_key: str,
        request_hash: str,
        response_data: dict | None = None,
        status_code: int | None = None
    ) -> tuple[bool, dict | None]:
        """
        Check idempotency and store response if new.
        
        Returns:
            tuple: (is_duplicate, cached_response)
        """
        key_record = await self.get_or_create_idempotency_key(user_id, idempotency_key)
        if not key_record:
            return False, None
        
        # If already processed, return cached response
        if key_record.response_data:
            return True, key_record.response_data
        
        # Store request hash and response for future idempotent requests
        key_record.request_hash = request_hash
        key_record.response_data = response_data
        key_record.status_code = status_code
        key_record.processed_at = datetime.now(UTC)
        
        return False, None


def generate_request_hash(payload: dict) -> str:
    """Generate SHA256 hash of request payload for idempotency validation."""
    import json
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


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
            last_error: Exception | None = None
            for attempt in range(MAX_RETRIES):
                try:
                    response = await client.post(
                        f"{self.BASE_URL}/payments",
                        auth=(self.shop_id, self.secret_key),
                        headers={
                            "Content-Type": "application/json",
                            "Idempotence-Key": idempotency_key or f"payment_{datetime.now(UTC).timestamp()}",
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
                except (httpx.HTTPError, httpx.TimeoutException) as e:
                    last_error = e
                    if attempt < MAX_RETRIES - 1:
                        delay = RETRY_BASE_DELAY * (2 ** attempt)
                        logger.warning("YooKassa create_payment retry %d/%d after %s: %s", attempt + 1, MAX_RETRIES, delay, e)
                        await asyncio.sleep(delay)
                    else:
                        raise ValidationException(f"YooKassa API failed after {MAX_RETRIES} retries: {e}") from e
            raise ValidationException(f"YooKassa API failed: {last_error}") from last_error

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
        wallet.updated_at = datetime.now(UTC)
        await self.db.commit()
        return WalletResponse.model_validate(wallet)

    async def debit(self, user_id: UUID, amount: float) -> WalletResponse:
        from app.models.payment import Wallet

        result = await self.db.execute(
            Wallet.__table__.update()
            .where(Wallet.user_id == user_id, Wallet.balance_rub >= amount)
            .values(balance_rub=Wallet.balance_rub - amount)
            .returning(Wallet)
        )
        updated = result.one_or_none()
        if updated is None:
            raise ValidationException("Недостаточно средств на кошельке")
        return WalletResponse.model_validate(updated)

    async def debit_bonus(self, user_id: UUID, amount: float) -> WalletResponse:
        from app.models.payment import Wallet

        result = await self.db.execute(
            Wallet.__table__.update()
            .where(
                Wallet.user_id == user_id,
                Wallet.bonus_balance >= amount,
            )
            .values(bonus_balance=Wallet.bonus_balance - amount)
            .execution_options(synchronize_session="fetch")
            .returning(Wallet)
        )
        updated = result.one_or_none()
        if updated is None:
            raise ValidationException("Недостаточно бонусных средств на кошельке")
        return WalletResponse.model_validate(updated)


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.wallet_repo = WalletRepository(db)
        self.yookassa = YooKassaClient()
        self.wallet_service = WalletService(db)
        self.idempotency_service = IdempotencyService(db)

    async def create_payment(
        self, 
        user_id: UUID, 
        project_id: UUID, 
        amount: float, 
        method: str = "bank_card",
        idempotency_key: str | None = None
    ) -> PaymentResponse:
        """
        Create payment with idempotency support.
        
        Args:
            user_id: User ID
            project_id: Project ID to pay for
            amount: Payment amount in RUB
            method: Payment method
            idempotency_key: Optional key for idempotent requests
        
        Returns:
            PaymentResponse with payment details and confirmation URL
        """
        # Generate idempotency key if not provided
        if idempotency_key is None:
            idempotency_key = f"{user_id}:{project_id}:{datetime.now(UTC).timestamp()}"
        
        # Prepare request payload for hashing
        request_payload = {
            "user_id": str(user_id),
            "project_id": str(project_id),
            "amount": amount,
            "method": method
        }
        request_hash = generate_request_hash(request_payload)
        
        # Check for duplicate request
        is_duplicate, cached_response = await self.idempotency_service.check_and_set_idempotency(
            user_id=user_id,
            idempotency_key=idempotency_key,
            request_hash=request_hash
        )
        
        if is_duplicate and cached_response:
            # Return cached response for duplicate request
            return PaymentResponse(**cached_response)
        
        # Check for existing paid project
        from app.repositories.projects import ProjectRepository
        project_repo = ProjectRepository(self.db)
        project = await project_repo.get_by_id(project_id, user_id)
        if project is None:
            raise NotFoundException("Проект не найден")
        
        if project.paid_rub and project.paid_rub > 0:
            raise ConflictException("Оплата для этого проекта уже существует")
        
        # Check for existing successful payment
        from sqlalchemy import select
        from app.models.payment import Payment as PaymentModel
        existing_paid = await self.db.execute(
            select(PaymentModel).where(
                PaymentModel.project_id == project_id,
                PaymentModel.user_id == user_id,
                PaymentModel.status == "paid",
            )
        )
        if existing_paid.scalar_one_or_none() is not None:
            raise ConflictException("Оплата для этого проекта уже существует")
        
        # Create new payment record
        payment = PaymentModel(
            user_id=user_id,
            project_id=project_id,
            provider_id=UUID(int=0),
            status="pending",
            method=method,
            amount_rub=amount,
            bonus_amount_rub=0,
            discount_rub=0,
            provider_payload={},
            idempotency_key=idempotency_key,
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
        payment.provider_payload = yookassa_payment
        confirmation_url = yookassa_payment.get("confirmation", {}).get("confirmation_url")
        
        # Build response
        response_data = {
            "id": str(payment.id),
            "user_id": str(payment.user_id),
            "project_id": str(payment.project_id),
            "status": payment.status,
            "amount_rub": payment.amount_rub,
            "method": payment.method,
            "created_at": payment.created_at,
        }
        if confirmation_url:
            response_data["confirmation_url"] = confirmation_url
        
        # Store response for idempotency
        await self.idempotency_service.check_and_set_idempotency(
            user_id=user_id,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            response_data=response_data,
            status_code=200
        )
        
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
            if payment.status != "paid":
                payment.status = "paid"
                paid_at = datetime.now(UTC)
                payment.paid_at = paid_at
                await self.wallet_service.credit(payment.user_id, payment.amount_rub)

                from app.services.referrals.service import ReferralService
                referral_service = ReferralService(self.db)
                await referral_service.mark_referral_completed(payment.user_id)
        elif event == "payment.canceled" or status == "canceled":
            payment.status = "failed"
        elif event == "payment.waiting_for_capture" or status == "waiting_for_capture":
            payment.status = "authorized"

        await self.db.commit()
        return {"received": True, "payment_id": str(payment.id), "status": payment.status}

    async def get_payment(self, payment_id: UUID, user_id: UUID | None = None) -> PaymentResponse:
        payment = await self.payment_repo.get_by_id(payment_id)
        if payment is None:
            raise NotFoundException("Платёж не найден")
        if user_id is not None and payment.user_id != user_id:
            raise NotFoundException("Платёж не найден")
        return PaymentResponse.model_validate(payment)
