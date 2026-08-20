"""Integration tests for admin endpoints to improve coverage."""
from uuid import uuid4

import pytest

from app.core.security import create_access_token


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
async def admin_headers(admin_user):
    token = create_access_token(admin_user.id)
    return {"Authorization": f"Bearer {token}", "X-Requested-With": "XMLHttpRequest"}


@pytest.mark.asyncio
async def test_admin_get_stats(client, db_session, admin_headers):
    """GET /admin/stats returns dashboard stats."""
    response = await client.get("/api/v1/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_projects" in data
    assert "total_payments" in data


@pytest.mark.asyncio
async def test_admin_get_users(client, db_session, admin_headers, test_user):
    """GET /admin/users returns user list."""
    response = await client.get("/api/v1/admin/users", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_admin_get_templates(client, db_session, admin_headers):
    """GET /admin/templates returns template list."""
    response = await client.get("/api/v1/admin/templates", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_admin_get_queue(client, db_session, admin_headers):
    """GET /admin/queue returns queue jobs."""
    response = await client.get("/api/v1/admin/queue", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_admin_get_workers(client, db_session, admin_headers):
    """GET /admin/workers returns workers."""
    response = await client.get("/api/v1/admin/workers", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_admin_get_audit_logs(client, db_session, admin_headers):
    """GET /admin/audit-logs returns audit logs."""
    response = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_admin_get_orders(client, db_session, admin_headers):
    """GET /admin/orders returns orders."""
    response = await client.get("/api/v1/admin/orders", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_admin_get_payments(client, db_session, admin_headers):
    """GET /admin/payments returns payments."""
    response = await client.get("/api/v1/admin/payments", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_admin_access_forbidden_for_non_admin(client, db_session, test_user):
    """Non-admin users cannot access admin endpoints."""
    token = create_access_token(test_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/admin/stats", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_ledger_transactions(client, db_session, admin_headers, admin_user):
    """GET /admin/ledger/transactions returns ledger transactions."""
    from app.models.payment import LedgerTransaction, Wallet

    wallet = Wallet(user_id=admin_user.id, balance_rub=0, bonus_balance=0)
    db_session.add(wallet)
    await db_session.commit()

    tx = LedgerTransaction(
        user_id=admin_user.id,
        wallet_id=wallet.id,
        type="adjustment",
        amount_rub=100.0,
        is_bonus=False,
        reason="Test",
    )
    db_session.add(tx)
    await db_session.commit()

    response = await client.get("/api/v1/admin/ledger/transactions", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["transactions"][0]["type"] == "adjustment"


@pytest.mark.asyncio
async def test_admin_nonexistent_generation_detail(client, db_session, admin_headers):
    """GET /admin/generations/{id} returns 404 for nonexistent generation."""
    response = await client.get(f"/api/v1/admin/generations/{uuid4()}", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_nonexistent_order_detail(client, db_session, admin_headers):
    """GET /admin/orders/{id} returns 404 for nonexistent order."""
    response = await client.get(f"/api/v1/admin/orders/{uuid4()}", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_system_settings(client, db_session, admin_headers):
    """GET /admin/system/settings returns settings."""
    response = await client.get("/api/v1/admin/system/settings", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
