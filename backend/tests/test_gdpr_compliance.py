"""Integration tests for GDPR compliance — account deletion and data export."""

import pytest
from sqlalchemy import select

from app.models.audit import AuditLog
from app.models.generation import Generation
from app.models.payment import Payment, Wallet
from app.models.project import Project
from app.models.user import User, UserAuthIdentity, UserPreferences


@pytest.fixture
async def auth_headers(test_user):
    from app.core.security import create_access_token

    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}", "X-Requested-With": "XMLHttpRequest"}


@pytest.mark.asyncio
async def test_gdpr_export_returns_user_data(client, db_session, test_user, auth_headers):
    """GET /account/export returns comprehensive user data."""
    wallet = Wallet(user_id=test_user.id, balance_rub=500.0, bonus_balance=0.0)
    db_session.add(wallet)
    await db_session.commit()

    project = Project(
        owner_user_id=test_user.id,
        title="Test Project",
        occasion_code="birthday",
        price_rub=590.0,
    )
    db_session.add(project)
    await db_session.commit()

    payment = Payment(
        user_id=test_user.id,
        project_id=project.id,
        status="paid",
        method="bank_card",
        amount_rub=590.0,
    )
    db_session.add(payment)
    await db_session.commit()

    generation = Generation(
        project_id=project.id,
        type="video",
        status="completed",
    )
    db_session.add(generation)
    await db_session.commit()

    response = await client.get("/api/v1/account/export", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["user"]["email"] == test_user.email
    assert data["user"]["display_name"] == test_user.display_name
    assert "wallet" in data
    assert data["wallet"]["balance_rub"] == "500.0"
    assert len(data["payments"]) == 1
    assert data["payments"][0]["status"] == "paid"
    assert len(data["projects"]) == 1
    assert data["projects"][0]["title"] == "Test Project"
    assert len(data["generations"]) == 1
    assert data["generations"][0]["status"] == "completed"
    assert "audit_logs" in data


@pytest.mark.asyncio
async def test_gdpr_export_csv(client, db_session, test_user, auth_headers):
    """GET /account/export/{table_name} returns CSV."""
    payment = Payment(
        user_id=test_user.id,
        project_id=None,
        status="paid",
        method="bank_card",
        amount_rub=590.0,
    )
    db_session.add(payment)
    await db_session.commit()

    response = await client.get("/api/v1/account/export/payments", headers=auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    content = response.text
    assert "id" in content
    assert "amount_rub" in content


@pytest.mark.asyncio
async def test_gdpr_export_invalid_table(client, db_session, test_user, auth_headers):
    """Invalid table name returns empty CSV."""
    response = await client.get("/api/v1/account/export/invalid_table", headers=auth_headers)
    assert response.status_code == 200
    assert response.text == ""


@pytest.mark.asyncio
async def test_account_deletion_request(client, db_session, test_user, auth_headers):
    """POST /account/delete-request anonymizes user data."""
    assert test_user.email is not None
    assert test_user.deleted_at is None

    response = await client.post("/api/v1/account/delete-request", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["deleted"] is True
    assert data["scheduled"] is False

    await db_session.refresh(test_user)
    assert test_user.deleted_at is not None
    assert test_user.email is None
    assert test_user.phone is None
    assert test_user.display_name is not None
    assert test_user.status == "deleted"


@pytest.mark.asyncio
async def test_account_deletion_soft_delete(client, db_session, test_user, auth_headers):
    """DELETE /account/me soft-deletes the account (anonymization)."""
    assert test_user.email is not None
    assert test_user.deleted_at is None

    response = await client.delete("/api/v1/account/me", headers=auth_headers)
    assert response.status_code == 204

    await db_session.refresh(test_user)
    assert test_user.deleted_at is not None
    assert test_user.email is None
    assert test_user.phone is None
    assert test_user.display_name is None


@pytest.mark.asyncio
async def test_account_hard_delete_requires_admin(client, db_session, test_user, auth_headers):
    """DELETE /account/me/hard requires admin privileges."""
    response = await client.delete("/api/v1/account/me/hard", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_account_hard_delete_admin(
    client, db_session, test_user, auth_headers
):
    """DELETE /account/me/hard works for admin users."""
    from app.core.security import create_access_token

    test_user.is_admin = True
    await db_session.commit()

    token = create_access_token(test_user.id)
    admin_headers = {"Authorization": f"Bearer {token}", "X-Requested-With": "XMLHttpRequest"}

    project = Project(
        owner_user_id=test_user.id,
        title="Test Project",
        occasion_code="birthday",
        price_rub=590.0,
    )
    db_session.add(project)
    await db_session.commit()

    payment = Payment(
        user_id=test_user.id,
        project_id=project.id,
        status="paid",
        method="bank_card",
        amount_rub=590.0,
    )
    db_session.add(payment)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.id == test_user.id))
    user_before = result.scalar_one()
    assert user_before is not None

    response = await client.delete("/api/v1/account/me/hard", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["deleted"] is True
    assert data["audit_log_count"] >= 0

    result_after = await db_session.execute(select(User).where(User.id == test_user.id))
    user_after = result_after.scalar_one_or_none()
    assert user_after is None


@pytest.mark.asyncio
async def test_gdpr_export_includes_recipients(
    client, db_session, test_user, auth_headers
):
    """Data export includes recipient data."""
    from app.models.recipient import Recipient

    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="John",
        last_name="Doe",
        relationship="friend",
        contact_phone="+1234567890",
    )
    db_session.add(recipient)
    await db_session.commit()

    response = await client.get("/api/v1/account/export", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "recipients" in data
    assert len(data["recipients"]) == 1
    assert data["recipients"][0]["first_name"] == "John"


@pytest.mark.asyncio
async def test_gdpr_export_includes_preferences(
    client, db_session, test_user, auth_headers
):
    """Data export includes user preferences."""

    prefs = UserPreferences(
        user_id=test_user.id,
        preferred_moods=["tears", "laugh"],
        preferred_styles=["cinematic"],
        marketing_opt_in=False,
        analytics_opt_in=True,
    )
    db_session.add(prefs)
    await db_session.commit()

    response = await client.get("/api/v1/account/export", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "preferences" in data
    assert data["preferences"]["marketing_opt_in"] is False
    assert data["preferences"]["analytics_opt_in"] is True


@pytest.mark.asyncio
async def test_gdpr_export_includes_auth_identities(
    client, db_session, test_user, auth_headers
):
    """Data export includes auth identity data."""
    identity = UserAuthIdentity(
        user_id=test_user.id,
        provider="email",
        provider_user_id=f"auth_{test_user.id}",
        email=test_user.email,
    )
    db_session.add(identity)
    await db_session.commit()

    response = await client.get("/api/v1/account/export", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "auth_identities" in data
    assert len(data["auth_identities"]) == 1
    assert data["auth_identities"][0]["provider"] == "email"


@pytest.mark.asyncio
async def test_account_deletion_logs_audit(
    client, db_session, test_user, auth_headers
):
    """Account deletion creates an audit log entry."""
    response = await client.delete("/api/v1/account/me", headers=auth_headers)
    assert response.status_code == 204

    result = await db_session.execute(
        select(AuditLog).where(AuditLog.actor_user_id == test_user.id)
    )
    logs = result.scalars().all()
    assert len(logs) >= 1
    assert logs[0].action == "account_deletion"


@pytest.mark.asyncio
async def test_gdpr_export_requires_auth(client, db_session):
    """Unauthenticated export request returns 401."""
    response = await client.get("/api/v1/account/export")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_account_deletion_idempotent(
    client, db_session, test_user, auth_headers
):
    """Soft delete is idempotent — calling twice doesn't error."""
    response1 = await client.delete("/api/v1/account/me", headers=auth_headers)
    assert response1.status_code == 204

    response2 = await client.delete("/api/v1/account/me", headers=auth_headers)
    assert response2.status_code == 204

    await db_session.refresh(test_user)
    assert test_user.email is None
    assert test_user.deleted_at is not None
