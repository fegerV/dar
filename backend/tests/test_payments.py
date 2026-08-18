"""Basic payment endpoint tests."""
import pytest
from uuid import uuid4

from app.core.exceptions import NotFoundException
from app.services.payments.service import PaymentService


@pytest.mark.asyncio
async def test_get_payment_not_found(db_session):
    service = PaymentService(db_session)
    with pytest.raises(NotFoundException):
        await service.get_payment(uuid4())


@pytest.mark.asyncio
async def test_get_payment_idor_check(db_session, test_user):
    from app.models.payment import Payment

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
