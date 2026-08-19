# Business Logic Security Audit

**Date:** 2026-08-19  
**Scope:** Business logic vulnerabilities across ACCOUNT, WALLET, PAYMENT, BONUS, GENERATION, LIMITS, SUBSCRIPTION, COUPONS, REFERRALS, FILES, SHARING

---

## Methodology

Traced each entity through the full request lifecycle: frontend DTO → API endpoint → service layer → repository → database → worker → storage → external API.

For each vulnerability identified: attack scenario, precondition, current behavior, expected behavior, impact, fix, and test.

---

## Vulnerability 1: Free Generation — price_rub Always 0

| Field | Value |
|---|---|
| **Entity** | Payment / Project |
| **Severity** | 🔴 CRITICAL |
| **Type** | Business logic bypass — free service |

**Attack Scenario:**
```
User registers → creates project → calls POST /pricing/calculate → gets PriceResponse with total_rub=590.00
→ calls POST /payments/projects/{id} → PaymentService.create_payment() uses project.price_rub (which is 0)
→ YooKassa processes payment for 0.00 RUB
→ User gets generation + payment record shows 0.00 paid
```

**Precondition:**
- User registered
- User has a project

**Current Behavior:**
- `Project.price_rub` defaults to `0` (model line 31: `default=0`)
- `ProjectCreate` schema (`schemas/project.py:7-11`) does NOT include `price_rub` — cannot be set on creation
- `ProjectUpdate` schema (`schemas/project.py:14-16`) only allows `title` and `requested_delivery_at` — cannot be updated
- `PricingService.calculate_price()` computes a price but **never writes it back** to `project.price_rub`
- `PaymentService.create_payment()` charges `float(project.price_rub)` which is always `0.0`

**Expected Behavior:**
- `PricingService.calculate_price()` should write the calculated price to `project.price_rub`
- OR `PaymentService.create_payment()` should accept the calculated price from the frontend
- OR `ProjectCreate` should accept an initial price

**Impact:** Every user can generate unlimited videos for free. Complete revenue bypass.

**Fix:** Update `PaymentService.create_payment()` to accept an explicitly calculated amount from the frontend, or have `PricingService` persist `project.price_rub`.

**Test:**
```python
async def test_payment_charges_calculated_amount(client, auth_headers, test_user, db_session):
    # Create project
    project = await client.post("/api/v1/projects", json={"recipient_id": ..., "occasion_code": "birthday"}, headers=auth_headers)
    project_id = project.json()["id"]
    # Calculate price
    price = await client.post("/api/v1/pricing/calculate", json={"project_id": project_id}, headers=auth_headers)
    # Create payment with calculated amount
    payment = await client.post(f"/api/v1/payments/projects/{project_id}", json={"method": "bank_card"}, headers=auth_headers)
    assert payment.json()["amount_rub"] > 0  # Currently fails — amount is 0.0
```

---

## Vulnerability 2: Welcome Entitlement Code Mismatch

| Field | Value |
|---|---|
| **Entity** | Account / Entitlement |
| **Severity** | 🔴 HIGH |
| **Type** | Business logic bypass — free entitlement never usable |

**Attack Scenario:**
```
User registers → AuthService.register() creates Entitlement(code="welcome_generation", quantity=1)
→ User creates project → calls POST /pricing/calculate
→ PricingService checks for Entitlement(code="free_generation") — not found
→ PricingService returns free_generation_available=false, total_rub=590.00
→ User pays full price for what should be a free generation
```

**Current Behavior:**
- `AuthService.register()` (line 49): `code="welcome_generation"`
- `PricingService.calculate_price()` (line 69): checks `Entitlement.code == "free_generation"`
- Two different codes — the welcome entitlement is never matched

**Expected Behavior:**
- Both should use the same code, e.g., `"welcome_generation"`

**Impact:** New users who should get a free generation are charged full price. User-facing bug + revenue loss due to churn.

**Fix:** Change `PricingService.calculate_price()` line 69 to check for `"welcome_generation"` instead of `"free_generation"`.

---

## Vulnerability 3: Webhook Replay — Double Wallet Credit

| Field | Value |
|---|---|
| **Entity** | Payment / Wallet |
| **Severity** | 🔴 HIGH |
| **Type** | Race condition / idempotency bypass |

**Attack Scenario:**
```
1. User pays 590 RUB via YooKassa
2. YooKassa sends webhook → handler credits user's wallet 590 RUB
3. Network glitch — YooKassa retries the same webhook
4. Handler processes it again → wallet credited another 590 RUB
5. User now has 1180 RUB in wallet from a 590 RUB payment
```

**Precondition:**
- User has made at least one successful payment
- YooKassa retries the webhook (documented YooKassa behavior)

**Current Behavior:**
- `PaymentService.handle_webhook()` (line 167) does NOT check if the payment is already `status="paid"` before crediting the wallet
- Line 191-201: if event is `payment.succeeded`, wallet is credited unconditionally

**Expected Behavior:**
- Check `if payment.status != "paid"` before crediting wallet
- If already paid, return early without re-crediting

**Impact:** Users can get unlimited wallet credit by replaying webhooks.

**Fix:**
```python
if payment.status != "paid":
    payment.status = "paid"
    paid_at = datetime.now(timezone.utc)
    await self.wallet_service.credit(payment.user_id, payment.amount_rub)
```

**Test:**
```python
async def test_webhook_idempotency(client, db_session, test_user):
    # Simulate two webhook calls for the same payment
    payment = create_test_payment(db_session, test_user.id, status="pending")
    webhook_body = {"event": "payment.succeeded", "metadata": {"payment_id": str(payment.id)}, ...}
    # First webhook
    await service.handle_webhook(raw_body, webhook_body, valid_signature)
    assert wallet.balance_rub == 590
    # Second webhook (replay)
    await service.handle_webhook(raw_body, webhook_body, valid_signature)
    assert wallet.balance_rub == 590  # Should not increase
```

---

## Vulnerability 4: Entitlement Consumption Race Condition

| Field | Value |
|---|---|
| **Entity** | Entitlement |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Race condition — double spend |

**Attack Scenario:**
```
1. User has Entitlement(quantity=1, consumed=0)
2. Request A: GET /payments/entitlements/{id}/consume → reads consumed=0
3. Request B: GET /payments/entitlements/{id}/consume → reads consumed=0 (before A commits)
4. Request A: consumed=1, checks 1 <= 1 ✓, commits
5. Request B: consumed=1, checks 1 <= 1 ✓, commits
6. Both requests succeed — entitlement was consumed twice
```

**Precondition:**
- User has an entitlement with quantity > 0
- Two concurrent `consume_entitlement` requests are made

**Current Behavior:**
- `EntitlementRepository.consume()` (line 25): `entitlement.consumed += quantity` then `flush()` — no check before increment
- `EntitlementService.consume_entitlement()` (line 42): checks `if entitlement.consumed > entitlement.quantity` AFTER increment — too late

**Expected Behavior:**
- Use `UPDATE ... WHERE consumed + quantity <= quantity` atomic update
- Or use `SELECT FOR UPDATE` within a transaction

**Impact:** User can double-spend entitlements.

**Fix:**
```python
from sqlalchemy import func
result = await self.db.execute(
    Entitlement.__table__.update()
    .where(Entitlement.id == entitlement_id, Entitlement.user_id == user_id)
    .where(Entitlement.consumed + quantity <= Entitlement.quantity)
    .values(consumed=Entitlement.consumed + quantity)
    .returning(Entitlement)
)
```

---

## Vulnerability 5: Promo Code Always Valid

| Field | Value |
|---|---|
| **Entity** | Coupon / Payment |
| **Severity** | 🔴 HIGH |
| **Type** | Business logic bypass — free discount |

**Attack Scenario:**
```
User calls POST /pricing/promo/validate with body={"code": "anything"}
→ PricingService.validate_promo_code() always returns {"valid": true, "discount_rub": 100.00}
→ User gets 100 RUB discount for any random string
```

**Current Behavior:**
- `PricingService.validate_promo_code()` (line 90-96): Hardcoded return `valid=True, discount_rub=100.00`
- `_apply_promo_code()` (line 110-118): Also hardcoded `valid=True, discount_rub=min(100, price)`

**Expected Behavior:**
- Promo codes should be validated against a database table
- Invalid codes should return `valid=False`

**Impact:** Any user can get 100 RUB discount on every order by entering any promo code.

**Fix:**
- Create a `promo_codes` table in the database
- Implement `_apply_promo_code()` to query the database
- Remove the hardcoded return values

---

## Vulnerability 6: Generation Never Dispatched to Worker

| Field | Value |
|---|---|
| **Entity** | Generation |
| **Severity** | 🔴 CRITICAL |
| **Type** | Broken flow — generation never runs |

**Attack Scenario:**
```
User calls POST /generations/projects/{id} → GenerationService.start_generation() creates a GenerationJob with status="queued"
→ No Celery task is dispatched
→ Worker never picks up the job
→ Generation stays in "queued" status forever
→ SSE stream never emits progress events
```

**Current Behavior:**
- `GenerationService.start_generation()` (line 69-77): Creates `GenerationJob` but does NOT call `process_generation_job.apply_async()`
- The only `apply_async()` call is in `PipelineOrchestrator.run()` (line 186)
- The Android app calls `/generations/projects/{id}` (via `GenerationsApi.start()`), NOT `/pipeline/projects/{id}/run`

**Expected Behavior:**
- After creating the job, dispatch it to the worker:
  ```python
  process_generation_job.apply_async(args=[str(job.id)], countdown=5)
  ```

**Impact:** No user can actually generate any video. The entire core business flow is broken.

**Fix:** Add task dispatch after job creation in `GenerationService.start_generation()`.

---

## Vulnerability 7: `generation.prompt` AttributeError in Worker

| Field | Value |
|---|---|
| **Entity** | Generation / Quality |
| **Severity** | 🔴 CRITICAL |
| **Type** | Runtime crash — AttributeError |

**Attack Scenario:**
```
If execute_pipeline were dispatched:
→ Worker calls QualityCheckRequest(prompt=generation.prompt)
→ Generation model has NO "prompt" attribute → AttributeError
→ Generation stuck in "processing" status
```

**Current Behavior:**
- `pipeline_tasks.py:132`: `QualityCheckRequest(prompt=generation.prompt)` — `Generation` model has no `prompt` field
- `generation_tasks.py:83`: Uses safe `(generation.input_json or {}).get("prompt", "")`

**Expected Behavior:**
- Use `generation.input_json.get("prompt")` consistently

**Fix:** Replace `generation.prompt` with `(generation.input_json or {}).get("prompt", "")` in `pipeline_tasks.py:132`.

---

## Vulnerability 8: Telegram Linking is a Stub

| Field | Value |
|---|---|
| **Entity** | Telegram / Notification |
| **Severity** | 🔴 HIGH |
| **Type** | Incomplete feature — data not persisted |

**Attack Scenario:**
```
User calls POST /telegram/link with body={"telegram_id": 12345, "username": "user"}
→ Endpoint returns {"telegram_id": 12345, "username": "user", "status": "linked"}
→ Nothing is stored in the database
→ User tries to send video to Telegram → TelegramDeliveryService.send() → "Telegram chat_id missing"
```

**Current Behavior:**
- `POST /telegram/link` (line 18-28): Returns input data, does not persist
- `User` model has no `telegram_user_id` field
- `TelegramDeliveryService.send()` (line 26): `chat_id = delivery.destination` — relies on `destination` being set, which it isn't

**Expected Behavior:**
- `User` model should have `telegram_user_id` field
- `link_telegram` should store the ID on the user record
- `TelegramDeliveryService` should use the stored ID

**Fix:**
1. Add `telegram_user_id` column to `users` model + migration
2. Store `telegram_user_id` in `link_telegram()` endpoint
3. Update `TelegramDeliveryService` to fetch from user record

---

## Vulnerability 9: Referral Bonus Never Granted

| Field | Value |
|---|---|
| **Entity** | Referral / Bonus |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Unimplemented feature — bonus not granted |

**Attack Scenario:**
```
User A creates referral code
→ User B applies it → Referral(status="pending") created
→ User B completes a generation (pays)
→ mark_referral_completed is never called
→ User A and User B never receive bonus entitlements
```

**Current Behavior:**
- `ReferralService.mark_referral_completed()` exists (line 63) but is **never called from any code path**
- `referrer_bonus_granted` and `referee_bonus_granted` flags are never set to `true`

**Expected Behavior:**
- When a referred user completes their first paid generation, call `mark_referral_completed`
- Grant bonus entitlements to both referrer and referee

---

## Vulnerability 10: Free-Use Generation Bypass

| Field | Value |
|---|---|
| **Entity** | Payment / Generation |
| **Severity** | 🔴 CRITICAL |
| **Type** | Business logic bypass — no payment required |

**Attack Scenario:**
```
User registers → gets welcome_generation entitlement
→ Skips payment entirely → calls POST /generations/projects/{id}
→ Generation is created and (if dispatched) would run
→ User gets video without paying
```

**Current Behavior:**
- `GenerationService.start_generation()` does NOT check if the user has paid
- `payment.price_rub` is 0 (see Vulnerability 1), so payment always succeeds for 0 RUB
- No check that payment status is `"paid"` before allowing generation

**Expected Behavior:**
- `start_generation()` should verify that the project has a paid generation
- Check `payment.status == "paid"` for this project

**Fix:**
```python
# In GenerationService.start_generation()
payment = await PaymentRepository(db).get_by_project_id(project_id)
if payment is None or payment.status != "paid":
    raise ValidationException("Payment required before generation")
```

---

## Summary Table

| # | Vulnerability | Severity | Entity | Status |
|---|---|---|---|---|
| 1 | price_rub always 0 → free generation | 🔴 CRITICAL | Payment/Project | ✅ FIXED |
| 2 | Entitlement code mismatch → free entitlement unusable | 🔴 HIGH | Account/Entitlement | ✅ FIXED |
| 3 | Webhook replay → double wallet credit | 🔴 HIGH | Payment/Wallet | ✅ FIXED |
| 4 | Entitlement consumption race condition | ⚠️ MEDIUM | Entitlement | CONFIRMED |
| 5 | Promo code always valid | 🔴 HIGH | Coupon | CONFIRMED |
| 6 | Generation never dispatched to worker | 🔴 CRITICAL | Generation | ✅ FIXED |
| 7 | `generation.prompt` AttributeError in worker | 🔴 CRITICAL | Generation/Quality | ✅ FIXED |
| 8 | Telegram linking is a stub | 🔴 HIGH | Notification | ✅ FIXED |
| 9 | Referral bonus never granted | ⚠️ MEDIUM | Referral/Bonus | CONFIRMED |
| 10 | No payment check before generation | 🔴 CRITICAL | Payment/Generation | CONFIRMED |

---

## Priority Fix Order — IN PROGRESS

1. ✅ **Fix generation dispatch** (Vuln #6) — COMPLETED
2. ✅ **Fix `generation.prompt` crash** (Vuln #7) — COMPLETED
3. ⏳ **Fix payment enforcement** (Vuln #10) — PENDING
4. ✅ **Fix price persistence** (Vuln #1) — `calculate_price()` now writes to `project.price_rub`
5. ✅ **Fix webhook idempotency** (Vuln #3) — Added `if payment.status != "paid"` guard
6. ✅ **Fix entitlement code mismatch** (Vuln #2) — Changed `"free_generation"` → `"welcome_generation"`
7. ⏳ **Fix promo code validation** (Vuln #5) — PENDING
8. ✅ **Fix Telegram linking** (Vuln #8) — COMPLETED
9. ⏳ **Fix referral bonus** (Vuln #9) — PENDING
10. ⏳ **Fix entitlement race condition** (Vuln #4) — PENDING
