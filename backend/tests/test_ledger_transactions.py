"""Integration tests for ledger transaction listing API."""
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import delete

from app.models.payment import LedgerTransaction, Wallet
from app.services.admin.service import AdminService


@pytest.fixture(autouse=True)
async def _clean_ledger_transactions(db_session):
    await db_session.execute(delete(LedgerTransaction))
    await db_session.commit()



@pytest.fixture
async def admin_user(db_session):
    from app.models.user import User

    user = User(
        email=f"admin_{uuid4().hex[:8]}@example.com",
        display_name="Admin User",
        is_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_token(admin_user):
    from app.core.security import create_access_token

    return create_access_token(admin_user.id)


@pytest.fixture
async def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "X-Requested-With": "XMLHttpRequest"}


@pytest.fixture
async def user_with_wallet(db_session, test_user):
    wallet = Wallet(user_id=test_user.id, balance_rub=1000.0, bonus_balance=0.0)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)
    return wallet


@pytest.mark.asyncio
async def test_list_ledger_transactions_returns_paginated(
    client, db_session, admin_headers, test_user, user_with_wallet
):
    """Ledger transaction listing API returns paginated transactions."""
    now = datetime.now(UTC)
    tx1 = LedgerTransaction(
        user_id=test_user.id,
        wallet_id=user_with_wallet.id,
        type="adjustment",
        amount_rub=500.0,
        is_bonus=False,
        reason="Test adjustment 1",
        created_at=now,
    )
    tx2 = LedgerTransaction(
        user_id=test_user.id,
        wallet_id=user_with_wallet.id,
        type="bonus",
        amount_rub=100.0,
        is_bonus=True,
        reason="Test bonus 1",
        created_at=now + timedelta(seconds=1),
    )
    db_session.add_all([tx1, tx2])
    await db_session.commit()

    response = await client.get("/api/v1/admin/ledger/transactions", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["transactions"]) == 2
    assert data["transactions"][0]["id"] == str(tx2.id)
    assert data["transactions"][0]["type"] == "bonus"
    assert data["transactions"][0]["amount_rub"] == 100.0
    assert data["transactions"][0]["is_bonus"] is True
    assert data["transactions"][0]["user_id"] == str(test_user.id)
    assert data["transactions"][0]["user_email"] == test_user.email
    assert data["transactions"][1]["id"] == str(tx1.id)


@pytest.mark.asyncio
async def test_list_ledger_transactions_filter_by_type(
    client, db_session, admin_headers, test_user, user_with_wallet
):
    """Filter transactions by type."""
    txs = [
        LedgerTransaction(
            user_id=test_user.id,
            wallet_id=user_with_wallet.id,
            type="adjustment",
            amount_rub=500.0,
            is_bonus=False,
            reason="Adjustment",
            created_at=datetime.now(UTC),
        ),
        LedgerTransaction(
            user_id=test_user.id,
            wallet_id=user_with_wallet.id,
            type="bonus",
            amount_rub=100.0,
            is_bonus=True,
            reason="Bonus",
            created_at=datetime.now(UTC) + timedelta(seconds=1),
        ),
        LedgerTransaction(
            user_id=test_user.id,
            wallet_id=user_with_wallet.id,
            type="refund",
            amount_rub=200.0,
            is_bonus=False,
            reason="Refund",
            created_at=datetime.now(UTC) + timedelta(seconds=2),
        ),
    ]
    db_session.add_all(txs)
    await db_session.commit()

    params = {"transaction_type": "bonus"}
    response = await client.get(
        "/api/v1/admin/ledger/transactions",
        params=params,
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["transactions"][0]["type"] == "bonus"


@pytest.mark.asyncio
async def test_list_ledger_transactions_pagination(
    client, db_session, admin_headers, test_user, user_with_wallet
):
    """Pagination works correctly."""
    txs = []
    base = datetime.now(UTC)
    for i in range(5):
        txs.append(
            LedgerTransaction(
                user_id=test_user.id,
                wallet_id=user_with_wallet.id,
                type="adjustment",
                amount_rub=float(i * 100),
                is_bonus=False,
                reason=f"Adjustment {i}",
                created_at=base + timedelta(seconds=i),
            )
        )
    db_session.add_all(txs)
    await db_session.commit()

    params = {"page": "2", "page_size": "2"}
    response = await client.get(
        "/api/v1/admin/ledger/transactions",
        params=params,
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["page"] == 2
    assert data["page_size"] == 2
    assert len(data["transactions"]) == 2


@pytest.mark.asyncio
async def test_list_ledger_transactions_requires_admin(
    client, db_session, test_user
):
    """Non-admin users get 403."""
    from app.core.security import create_access_token

    token = create_access_token(test_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/admin/ledger/transactions", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_ledger_transactions_empty(
    client, db_session, admin_headers
):
    """Empty ledger returns empty list."""
    response = await client.get("/api/v1/admin/ledger/transactions", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["transactions"] == []


@pytest.mark.asyncio
async def test_list_ledger_transactions_includes_reference_and_admin(
    client, db_session, admin_headers, test_user, user_with_wallet, admin_user
):
    """Ledger transaction with reference_id and admin_id is included."""
    ref_uuid = uuid4()
    tx = LedgerTransaction(
        user_id=test_user.id,
        wallet_id=user_with_wallet.id,
        type="refund",
        amount_rub=250.0,
        is_bonus=False,
        admin_id=admin_user.id,
        reason="Admin refund",
        reference_id=ref_uuid,
        created_at=datetime.now(UTC),
    )
    db_session.add(tx)
    await db_session.commit()

    response = await client.get("/api/v1/admin/ledger/transactions", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    tx_data = data["transactions"][0]
    assert tx_data["admin_id"] == str(admin_user.id)
    assert tx_data["reference_id"] == str(ref_uuid)
    assert tx_data["reason"] == "Admin refund"


@pytest.mark.asyncio
async def test_list_ledger_service_directly(
    db_session, admin_headers, test_user, user_with_wallet
):
    """AdminService.list_ledger_transactions returns correct structure."""
    tx = LedgerTransaction(
        user_id=test_user.id,
        wallet_id=user_with_wallet.id,
        type="penalty",
        amount_rub=50.0,
        is_bonus=False,
        reason="Penalty",
        created_at=datetime.now(UTC),
    )
    db_session.add(tx)
    await db_session.commit()

    service = AdminService(db_session)
    result = await service.list_ledger_transactions(page=1, page_size=10)
    assert result.total == 1
    assert result.page == 1
    assert result.page_size == 10
    assert len(result.transactions) == 1
    assert result.transactions[0].type == "penalty"
    assert result.transactions[0].amount_rub == 50.0
    assert result.transactions[0].user_email == test_user.email
