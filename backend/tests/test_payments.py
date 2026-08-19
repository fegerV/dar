"""Basic payment endpoint tests."""
from uuid import uuid4

import pytest

from app.core.exceptions import NotFoundException, ValidationException
from app.models.payment import Payment, Wallet
from app.services.payments.service import PaymentService


@pytest.mark.asyncio
async def test_webhook_idempotency(db_session, test_user):
    """VULN-03: Webhook replay should not double-credit wallet."""

    from app.models.payment import Payment as PaymentModel

    wallet = Wallet(user_id=test_user.id, balance_rub=0, bonus_balance=0)
    db_session.add(wallet)
    await db_session.commit()

    payment = PaymentModel(
        user_id=test_user.id,
        project_id=None,
        provider_id=uuid4(),
        status="pending",
        method="bank_card",
        amount_rub=590.0,
        bonus_amount_rub=0,
        discount_rub=0,
        provider_payload={},
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)

    service = PaymentService(db_session)

    # Mock webhook signature verification for test
    service.yookassa.verify_webhook_signature = lambda body, sig: True

    webhook_body = {
        "event": "payment.succeeded",
        "metadata": {"payment_id": str(payment.id)},
        "object": {"id": "ext_123", "status": "succeeded"},
    }

    # First webhook call — should credit wallet
    await service.handle_webhook(
        raw_body=b"{}",
        body=webhook_body,
        signature="mock_signature",
    )
    wallet_after_first = await service.wallet_service.get_wallet(test_user.id)
    assert wallet_after_first.balance_rub == 590.0

    # Second webhook (replay) — should NOT re-credit
    await service.handle_webhook(
        raw_body=b"{}",
        body=webhook_body,
        signature="mock_signature",
    )
    wallet_after_second = await service.wallet_service.get_wallet(test_user.id)
    assert wallet_after_second.balance_rub == 590.0  # No double credit


@pytest.mark.asyncio
async def test_debit_atomic_no_overdraft(db_session, test_user):
    """VULN-03: Concurrent debits should not cause negative balance.

    With a shared session, the atomic UPDATE ensures the WHERE clause
    catches overspending attempts."""

    wallet = Wallet(user_id=test_user.id, balance_rub=100.0, bonus_balance=0)
    db_session.add(wallet)
    await db_session.commit()

    service = PaymentService(db_session)

    # First debit succeeds
    result1 = await service.wallet_service.debit(test_user.id, 100.0)
    assert result1.balance_rub == 0

    # Second debit for same amount should fail — insufficient funds
    with pytest.raises(ValidationException, match="Недостаточно средств"):
        await service.wallet_service.debit(test_user.id, 100.0)

    # Also test: cannot debit more than balance in a single call
    wallet2 = Wallet(user_id=uuid4(), balance_rub=50.0, bonus_balance=0)
    db_session.add(wallet2)
    await db_session.commit()
    with pytest.raises(ValidationException):
        await service.wallet_service.debit(wallet2.user_id, 100.0)


@pytest.mark.asyncio
async def test_get_payment_not_found(db_session):
    service = PaymentService(db_session)
    with pytest.raises(NotFoundException):
        await service.get_payment(uuid4())


@pytest.mark.asyncio
async def test_get_payment_idor_check(db_session, test_user):

    payment = Payment(
        user_id=uuid4(),  # different user
        project_id=None,
        provider_id=uuid4(),
        status="paid",
        method="bank_card",
        amount_rub=100.0,
        bonus_amount_rub=0,
        discount_rub=0,
        provider_payload={},
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)

    service = PaymentService(db_session)
    with pytest.raises(NotFoundException):
        await service.get_payment(payment.id, user_id=test_user.id)
