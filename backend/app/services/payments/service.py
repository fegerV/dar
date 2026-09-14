import asyncio
import hashlib
import hmac
import ipaddress
import logging
from datetime import UTC, datetime
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundException, ValidationException
from app.models.payment import Payment, Wallet
from app.repositories.storage import PaymentRepository, WalletRepository
from app.schemas.payment import PaymentResponse, WalletResponse

logger = logging.getLogger(__name__)
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0


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

    def allowed_ip_networks(self) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
        """Parse YOOKASSA_WEBHOOK_ALLOWED_IPS into network objects."""
        networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
        for chunk in settings.YOOKASSA_WEBHOOK_ALLOWED_IPS.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                networks.append(ipaddress.ip_network(chunk, strict=False))
            except ValueError:
                logger.warning("Invalid CIDR in YOOKASSA_WEBHOOK_ALLOWED_IPS: %s", chunk)
        return networks

    def verify_webhook_source(self, client_ip: str | None) -> bool:
        """Verify the notification originated from an official YooKassa IP range.

        YooKassa authenticates notifications by source IP, not by signature.
        Returns True when the allowlist is empty (check disabled).
        """
        networks = self.allowed_ip_networks()
        if not networks:
            return True
        if not client_ip:
            return False
        try:
            addr = ipaddress.ip_address(client_ip)
        except ValueError:
            return False
        return any(addr in net for net in networks)

    def verify_webhook_signature(self, body_bytes: bytes, signature: str | None) -> bool:
        # YooKassa does not sign notifications. HMAC is an optional extra layer
        # that only applies when YOOKASSA_WEBHOOK_SECRET is explicitly configured.
        if not self.webhook_secret:
            return True
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

    async def handle_webhook(
        self,
        raw_body: bytes,
        body: dict,
        signature: str | None = None,
        client_ip: str | None = None,
    ) -> dict:
        # 1) Source IP allowlist (the authentication method YooKassa actually uses).
        if settings.YOOKASSA_WEBHOOK_ENFORCE_IP and not self.yookassa.verify_webhook_source(client_ip):
            logger.warning("Rejected YooKassa webhook from untrusted IP: %s", client_ip)
            raise ValidationException("Webhook source IP is not allowed")

        # 2) Optional HMAC layer — only enforced when a secret is configured.
        if not self.yookassa.verify_webhook_signature(raw_body, signature):
            logger.warning("Rejected YooKassa webhook: invalid signature")
            raise ValidationException("Invalid webhook signature")

        event = body.get("event")
        payment_id = body.get("object", {}).get("id")
        status = body.get("object", {}).get("status")

        metadata_payment_id = body.get("metadata", {}).get("payment_id")
        payment = None
        if metadata_payment_id:
            try:
                payment = await self.payment_repo.get_by_id(UUID(metadata_payment_id))
            except (ValueError, AttributeError):
                payment = None
        if payment is None and payment_id:
            from sqlalchemy import select
            result = await self.db.execute(
                select(Payment).where(Payment.external_payment_id == payment_id)
            )
            payment = result.scalar_one_or_none()

        if payment is None:
            logger.warning("YooKassa webhook for unknown payment: %s", payment_id)
            return {"received": True, "status": "ignored"}

        payment.provider_payload = body
        paid_at = None

        if event == "payment.succeeded" or status == "succeeded":
            # Idempotency: never credit a wallet twice for the same payment.
            if payment.status == "paid":
                return {"received": True, "payment_id": str(payment.id), "status": "already_processed"}
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

        from app.services.webhooks import dispatch_webhook_event
        await dispatch_webhook_event(
            self.db,
            event or "payment.updated",
            {
                "payment_id": str(payment.id),
                "user_id": str(payment.user_id),
                "status": payment.status,
                "amount_rub": float(payment.amount_rub),
            },
        )

        return {"received": True, "payment_id": str(payment.id), "status": payment.status}

    async def get_payment(self, payment_id: UUID, user_id: UUID | None = None) -> PaymentResponse:
        payment = await self.payment_repo.get_by_id(payment_id)
        if payment is None:
            raise NotFoundException("Платёж не найден")
        if user_id is not None and payment.user_id != user_id:
            raise NotFoundException("Платёж не найден")
        return PaymentResponse.model_validate(payment)
