"""Integration tests for the completed MVP phases (Phase 1, 2.1-2.3, 3.1)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select, update

from core.config import get_settings
from models import Entitlement, Wallet, WalletTransaction


PWD = "password123"


async def register(client: AsyncClient, email: str) -> tuple[str, str]:
    reg = await client.post("/api/v1/auth/register", json={"email": email, "password": PWD})
    assert reg.status_code == 201, reg.text
    data = reg.json()
    return data["access_token"], data["user"]["id"]


async def make_recipient(client: AsyncClient, headers: dict) -> str:
    r = await client.post("/api/v1/recipients", headers=headers, json={
        "first_name": "Иван", "last_name": "Петров", "relationship_type": "friend",
        "interests": ["кино"], "traits": ["весёлый"],
    })
    assert r.status_code == 201
    return r.json()["id"]


async def make_priced_project(client: AsyncClient, headers: dict, recipient_id: str) -> str:
    p = await client.post("/api/v1/projects", headers=headers, json={
        "recipient_id": recipient_id, "occasion_code": "birthday", "title": "DR",
    })
    assert p.status_code == 201
    project_id = p.json()["id"]
    upd = await client.put(f"/api/v1/projects/{project_id}/brief", headers=headers, json={"desired_mood": "funny"})
    assert upd.json()["status"] == "in_progress"
    comp = await client.post(f"/api/v1/projects/{project_id}/brief/complete", headers=headers)
    assert comp.json()["status"] == "recommendations_ready"
    recs = (await client.get(f"/api/v1/projects/{project_id}/recommendations", headers=headers)).json()
    assert recs
    sel = await client.post(
        f"/api/v1/projects/{project_id}/recommendations/{recs[0]['id']}/select", headers=headers
    )
    assert sel.status_code == 200
    assert sel.json()["status"] == "template_selected"
    return project_id


class TestPhase1BriefAndScript:
    @pytest.mark.asyncio
    async def test_brief_state_machine(self, client: AsyncClient):
        token, _ = await register(client, "brief@example.com")
        h = {"Authorization": f"Bearer {token}"}
        rid = await make_recipient(client, h)
        p = await client.post("/api/v1/projects", headers=h, json={"recipient_id": rid, "occasion_code": "birthday"})
        assert p.status_code == 201
        assert p.json()["status"] == "briefing"
        upd = await client.put(f"/api/v1/projects/{p.json()['id']}/brief", headers=h, json={"desired_mood": "funny"})
        assert upd.json()["status"] == "in_progress"
        comp = await client.post(f"/api/v1/projects/{p.json()['id']}/brief/complete", headers=h)
        assert comp.json()["status"] == "recommendations_ready"

    @pytest.mark.asyncio
    async def test_script_generation_and_get(self, client: AsyncClient):
        token, _ = await register(client, "script@example.com")
        h = {"Authorization": f"Bearer {token}"}
        rid = await make_recipient(client, h)
        pid = await make_priced_project(client, h, rid)
        gen = await client.post(f"/api/v1/projects/{pid}/script", headers=h)
        assert gen.status_code == 201, gen.text
        body = gen.json()
        assert len(body["variants"]) == 3
        assert body["word_limit"] == 30
        assert body["suitable_for_lite"] is True
        for v in body["variants"]:
            assert 0 < v["word_count"] <= 30
        got = await client.get(f"/api/v1/projects/{pid}/script", headers=h)
        assert got.status_code == 200
        assert len(got.json()["variants"]) == 3


class TestPhase2Preview:
    @pytest.mark.asyncio
    async def test_preview_before_master_frame_is_404(self, client: AsyncClient):
        token, _ = await register(client, "preview1@example.com")
        h = {"Authorization": f"Bearer {token}"}
        rid = await make_recipient(client, h)
        p = await client.post("/api/v1/projects", headers=h, json={"recipient_id": rid, "occasion_code": "birthday"})
        pid = p.json()["id"]
        missing = await client.get(f"/api/v1/projects/{pid}/preview", headers=h)
        assert missing.status_code == 404

    @pytest.mark.asyncio
    async def test_preview_after_master_frame(self, client: AsyncClient):
        token, _ = await register(client, "preview2@example.com")
        h = {"Authorization": f"Bearer {token}"}
        rid = await make_recipient(client, h)
        p = await client.post("/api/v1/projects", headers=h, json={"recipient_id": rid, "occasion_code": "birthday"})
        pid = p.json()["id"]
        mf = await client.post(f"/api/v1/projects/{pid}/master-frame", headers=h, json={
            "concept": "cinematic", "prompt": "hero on red carpet", "width": 1024, "height": 1024,
        })
        assert mf.status_code == 201
        prev = await client.get(f"/api/v1/projects/{pid}/preview", headers=h)
        assert prev.status_code == 200
        data = prev.json()
        assert data["kind"] == "master_frame"
        assert data["watermarked"] is True
        assert data["preview_url"]


class TestPhase3Payment:
    @pytest.mark.asyncio
    async def test_free_payment_via_entitlement(self, client: AsyncClient):
        token, _ = await register(client, "free@example.com")
        h = {"Authorization": f"Bearer {token}"}
        rid = await make_recipient(client, h)
        pid = await make_priced_project(client, h, rid)
        price = await client.get(f"/api/v1/projects/{pid}/price", headers=h)
        assert price.status_code == 200
        pdata = price.json()
        assert pdata["free_generation_available"] is True
        assert float(pdata["total_rub"]) == 0
        pay = await client.post(f"/api/v1/projects/{pid}/payment", headers=h, json={"method": "mock"})
        assert pay.status_code == 201
        assert pay.json()["status"] == "paid"
        assert float(pay.json()["amount_rub"]) == 0
        proj = (await client.get(f"/api/v1/projects/{pid}", headers=h)).json()
        assert proj["status"] == "paid"

    @pytest.mark.asyncio
    async def test_topup_adds_balance(self, client: AsyncClient):
        token, _ = await register(client, "topup@example.com")
        h = {"Authorization": f"Bearer {token}"}
        r = await client.post("/api/v1/payments/topup", headers=h, json={"amount_rub": "500", "method": "mock"})
        assert r.status_code == 201
        assert r.json()["status"] == "paid"
        w = (await client.get("/api/v1/wallet", headers=h)).json()
        assert float(w["balance_rub"]) == 500
        assert float(w["bonus_balance"]) == 0

    @pytest.mark.asyncio
    async def test_webhook_rejects_bad_signature(self, client: AsyncClient):
        os.environ["YOOKASSA_SECRET_KEY"] = "test_secret"
        get_settings.cache_clear()
        body = b'{"event":"payment.succeeded","object":{"id":"x"}}'
        bad = await client.post(
            "/api/v1/payments/webhook", content=body,
            headers={"X-Yookassa-Signature": "bad", "Content-Type": "application/json"},
        )
        assert bad.status_code == 401
        del os.environ["YOOKASSA_SECRET_KEY"]
        get_settings.cache_clear()

    @pytest.mark.asyncio
    async def test_webhook_success_credits_cashback(self, client: AsyncClient, db_session):
        token, user_id = await register(client, "webhook@example.com")
        h = {"Authorization": f"Bearer {token}"}
        rid = await make_recipient(client, h)
        pid = await make_priced_project(client, h, rid)

        uid = uuid.UUID(user_id)
        # exhaust the 3 free-lite credits and seed a bonus balance directly
        await db_session.execute(
            update(Entitlement).where(Entitlement.user_id == uid, Entitlement.code == "free_lite")
            .values(consumed=3)
        )
        wallet = await db_session.scalar(select(Wallet).where(Wallet.user_id == uid))
        wallet.bonus_balance = Decimal("100")
        db_session.add(WalletTransaction(
            wallet_id=wallet.id, type="bonus_credit", amount_rub=Decimal("0"),
            bonus_amount_rub=Decimal("100"), balance_after_rub=Decimal("100"), description="seed bonus",
        ))
        await db_session.commit()

        # price now reflects bonus: 590 - min(100, 177) = 490
        price = (await client.get(f"/api/v1/projects/{pid}/price", headers=h)).json()
        assert float(price["total_rub"]) == 490
        assert float(price["bonus_used_rub"]) == 100

        pay = await client.post(f"/api/v1/projects/{pid}/payment", headers=h, json={"method": "mock"})
        assert pay.status_code == 201
        assert pay.json()["status"] == "pending"
        ext_id = pay.json()["external_payment_id"]

        os.environ["YOOKASSA_SECRET_KEY"] = "test_secret"
        get_settings.cache_clear()
        body = json.dumps({"event": "payment.succeeded", "object": {"id": ext_id}}).encode()
        sig = base64.b64encode(hmac.new(b"test_secret", body, hashlib.sha256).digest()).decode()
        wh = await client.post(
            "/api/v1/payments/webhook", content=body,
            headers={"X-Yookassa-Signature": sig, "Content-Type": "application/json"},
        )
        assert wh.status_code == 200, wh.text
        assert (await client.get(f"/api/v1/payments/{pay.json()['id']}", headers=h)).json()["status"] == "paid"
        # bonus 100 debited at payment success, +5% cashback of 490 = 24.50
        w = (await client.get("/api/v1/wallet", headers=h)).json()
        assert float(w["bonus_balance"]) == pytest.approx(24.50)
        del os.environ["YOOKASSA_SECRET_KEY"]
        get_settings.cache_clear()
