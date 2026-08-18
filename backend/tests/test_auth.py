"""Basic auth endpoint tests."""
import pytest

from app.core.security import hash_password


@pytest.mark.asyncio
async def test_register_and_login(client, db_session):
    response = await client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "password": "SecureP@ss",
        "display_name": "New User",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "user" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client, db_session):
    from app.models.user import User, UserAuthIdentity

    user = User(email="logintest@test.com", display_name="Login Test")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    identity = UserAuthIdentity(
        user_id=user.id,
        provider="email",
        provider_user_id="logintest@test.com",
        credentials_json={"password_hash": hash_password("CorrectPass123!")},
    )
    db_session.add(identity)
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json={
        "email": "logintest@test.com",
        "password": "WrongPass1",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
