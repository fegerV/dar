"""Integration tests for the user registration flow."""
from uuid import UUID

import pytest
from sqlalchemy import select


@pytest.mark.asyncio
async def test_register_creates_all_entities(client, db_session):
    from app.models.audit import AuditLog
    from app.models.email_verification import EmailVerification
    from app.models.payment import Entitlement, Wallet
    from app.models.referral import ReferralCode
    from app.models.user import User, UserPreferences

    response = await client.post("/api/v1/auth/register", json={
        "email": "complete@test.com",
        "password": "SecureP@ss1",
        "display_name": "Complete User",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    user_result = await db_session.execute(
        select(User).where(User.email == "complete@test.com")
    )
    user = user_result.scalar_one()

    wallet_result = await db_session.execute(
        select(Wallet).where(Wallet.user_id == user.id)
    )
    assert wallet_result.scalar_one() is not None

    prefs_result = await db_session.execute(
        select(UserPreferences).where(UserPreferences.user_id == user.id)
    )
    assert prefs_result.scalar_one() is not None

    entitlement_result = await db_session.execute(
        select(Entitlement).where(Entitlement.user_id == user.id)
    )
    entitlement = entitlement_result.scalar_one()
    assert entitlement.code == "welcome_generation"
    assert entitlement.quantity == 1

    referral_result = await db_session.execute(
        select(ReferralCode).where(ReferralCode.user_id == user.id)
    )
    assert referral_result.scalar_one() is not None

    verif_result = await db_session.execute(
        select(EmailVerification).where(EmailVerification.user_id == user.id)
    )
    verif = verif_result.scalar_one()
    assert verif.email == "complete@test.com"
    assert verif.verified is False
    assert verif.expires_at is not None

    audit_result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.actor_user_id == user.id,
            AuditLog.action == "user.registered",
        )
    )
    assert audit_result.scalar_one() is not None


@pytest.mark.asyncio
async def test_register_duplicate_email_conflict(client, db_session):
    payload = {
        "email": "duplicate@test.com",
        "password": "SecureP@ss1",
        "display_name": "First User",
    }
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    payload["display_name"] = "Second User"
    resp2 = await client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 409
    detail = resp2.json()["detail"]["error"]
    assert detail["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_register_duplicate_email_sequential(client, db_session):
    """Verify that the service-level duplicate check + DB constraint work together."""
    payload = {
        "email": "dup_seq@test.com",
        "password": "SecureP@ss1",
        "display_name": "First",
    }
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    payload["display_name"] = "Second"
    resp2 = await client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 409
    detail = resp2.json()["detail"]["error"]
    assert detail["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_register_invalid_password_too_short(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "short@test.com",
        "password": "Ab1!",
        "display_name": "Short",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_password_no_uppercase(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "nouppercase@test.com",
        "password": "securepass1!",
        "display_name": "NoUpper",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_password_no_digit(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "nodigit@test.com",
        "password": "SecurePassword!",
        "display_name": "NoDigit",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_password_no_special(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "nospecial@test.com",
        "password": "SecurePass123",
        "display_name": "NoSpecial",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_returns_valid_tokens(client, db_session):
    from app.core.security import decode_token

    response = await client.post("/api/v1/auth/register", json={
        "email": "tokens@test.com",
        "password": "SecureP@ss1",
        "display_name": "Token User",
    })
    assert response.status_code == 201
    data = response.json()

    access_payload = decode_token(data["access_token"])
    assert access_payload is not None
    assert access_payload["type"] == "access"

    refresh_payload = decode_token(data["refresh_token"])
    assert refresh_payload is not None
    assert refresh_payload["type"] == "refresh"


@pytest.mark.asyncio
async def test_register_response_includes_user(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "userfield@test.com",
        "password": "SecureP@ss1",
        "display_name": "User Field",
    })
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "userfield@test.com"
    assert data["user"]["display_name"] == "User Field"


@pytest.mark.asyncio
async def test_register_without_display_name(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "nodisplay@test.com",
        "password": "SecureP@ss1",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_register_email_verification_record(client, db_session):
    from sqlalchemy import select

    from app.models.email_verification import EmailVerification
    from app.models.user import User

    response = await client.post("/api/v1/auth/register", json={
        "email": "verify@test.com",
        "password": "SecureP@ss1",
        "display_name": "Verify User",
    })
    assert response.status_code == 201

    user_result = await db_session.execute(
        select(User).where(User.email == "verify@test.com")
    )
    user = user_result.scalar_one()


    verif_result = await db_session.execute(
        select(EmailVerification).where(EmailVerification.user_id == user.id)
    )
    verif = verif_result.scalar_one()

    assert verif.token_hash != ""
    assert verif.expires_at is not None


@pytest.mark.asyncio
async def test_register_referral_code_is_unique(client, db_session):
    from sqlalchemy import select

    from app.models.referral import ReferralCode

    codes = []
    for i in range(5):
        response = await client.post("/api/v1/auth/register", json={
            "email": f"referral{i}@test.com",
            "password": "SecureP@ss1",
            "display_name": f"User {i}",
        })
        assert response.status_code == 201
        user_data = response.json()
        user_id = UUID(user_data["user"]["id"])

        result = await db_session.execute(
            select(ReferralCode).where(ReferralCode.user_id == user_id)
        )
        code = result.scalar_one()
        assert code.code not in codes
        codes.append(code.code)
