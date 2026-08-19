"""Auth endpoint tests including token revocation, refresh rotation, and logout."""
import pytest

from app.core.security import hash_password


@pytest.mark.asyncio
async def test_register_and_login(client, db_session):
    response = await client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "password": "SecureP@ss1",
        "display_name": "New User",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
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


@pytest.mark.asyncio
async def test_password_policy_weak(client, db_session):
    response = await client.post("/api/v1/auth/register", json={
        "email": "weakpass@test.com",
        "password": "short",
        "display_name": "Weak",
    })
    assert response.status_code == 422
    detail = response.json()["detail"]
    if isinstance(detail, list):
        msg = detail[0]["msg"]
    else:
        msg = detail["error"]["message"]
    assert "Password" in msg or "character" in msg


@pytest.mark.asyncio
async def test_password_policy_no_complexity(client, db_session):
    response = await client.post("/api/v1/auth/register", json={
        "email": "noComplexity@test.com",
        "password": "alllowercase",
        "display_name": "NoComplexity",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token(client, db_session):
    from app.models.user import User, UserAuthIdentity

    user = User(email="refresh@test.com", display_name="Refresh User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    identity = UserAuthIdentity(
        user_id=user.id,
        provider="email",
        provider_user_id="refresh@test.com",
        credentials_json={"password_hash": hash_password("SecurePass1!")},
    )
    db_session.add(identity)
    await db_session.commit()

    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "refresh@test.com",
        "password": "SecurePass1!",
    })
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]

    refresh_resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert refresh_resp.status_code == 200
    refreshed = refresh_resp.json()
    assert "access_token" in refreshed
    assert refreshed["access_token"] != tokens["access_token"]


@pytest.mark.asyncio
async def test_refresh_token_revocation_after_use(client, db_session):
    from app.models.user import User, UserAuthIdentity

    user = User(email="rotate@test.com", display_name="Rotate User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    identity = UserAuthIdentity(
        user_id=user.id,
        provider="email",
        provider_user_id="rotate@test.com",
        credentials_json={"password_hash": hash_password("SecurePass1!")},
    )
    db_session.add(identity)
    await db_session.commit()

    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "rotate@test.com",
        "password": "SecurePass1!",
    })
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]

    # First refresh works
    r1 = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert r1.status_code == 200

    # Second refresh with same token fails (revoked)
    r2 = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert r2.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client, db_session):
    from app.models.user import User, UserAuthIdentity

    user = User(email="logout@test.com", display_name="Logout User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    identity = UserAuthIdentity(
        user_id=user.id,
        provider="email",
        provider_user_id="logout@test.com",
        credentials_json={"password_hash": hash_password("SecurePass1!")},
    )
    db_session.add(identity)
    await db_session.commit()

    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "logout@test.com",
        "password": "SecurePass1!",
    })
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]

    logout_resp = await client.post("/api/v1/auth/logout", json={
        "refresh_token": refresh_token,
    })
    assert logout_resp.status_code == 204

    refresh_resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert refresh_resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_used_as_access_token(client, db_session):
    from app.models.user import User, UserAuthIdentity

    user = User(email="forgery@test.com", display_name="Forgery User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    identity = UserAuthIdentity(
        user_id=user.id,
        provider="email",
        provider_user_id="forgery@test.com",
        credentials_json={"password_hash": hash_password("SecurePass1!")},
    )
    db_session.add(identity)
    await db_session.commit()

    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "forgery@test.com",
        "password": "SecurePass1!",
    })
    tokens = login_resp.json()

    # Use refresh token as access token — should fail
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_all_revokes_all_tokens(client, db_session):
    from app.models.user import User, UserAuthIdentity

    user = User(email="logoutall@test.com", display_name="Logout All User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    identity = UserAuthIdentity(
        user_id=user.id,
        provider="email",
        provider_user_id="logoutall@test.com",
        credentials_json={"password_hash": hash_password("SecurePass1!")},
    )
    db_session.add(identity)
    await db_session.commit()

    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "logoutall@test.com",
        "password": "SecurePass1!",
    })
    access_token = login_resp.json()["access_token"]
    refresh_token = login_resp.json()["refresh_token"]

    logout_resp = await client.post("/api/v1/auth/logout-all", headers={
        "Authorization": f"Bearer {access_token}",
    })
    assert logout_resp.status_code == 204

    refresh_resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert refresh_resp.status_code == 401


@pytest.mark.asyncio
async def test_login_rate_limiting(client, db_session):
    from app.models.user import User, UserAuthIdentity

    user = User(email="ratelimit@test.com", display_name="Rate Limit User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    identity = UserAuthIdentity(
        user_id=user.id,
        provider="email",
        provider_user_id="ratelimit@test.com",
        credentials_json={"password_hash": hash_password("SecurePass1!")},
    )
    db_session.add(identity)
    await db_session.commit()

    from app.middleware.rate_limit import _rate_store
    _rate_store.clear()

    for i in range(10):
        response = await client.post("/api/v1/auth/login", json={
            "email": "ratelimit@test.com",
            "password": "WrongPass1",
        })
        assert response.status_code == 401

    response = await client.post("/api/v1/auth/login", json={
        "email": "ratelimit@test.com",
        "password": "WrongPass1",
    })
    assert response.status_code == 429
