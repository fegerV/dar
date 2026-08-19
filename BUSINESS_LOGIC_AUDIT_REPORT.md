# Business Logic Security Audit Report

## Audit Methodology

Treated the attacker as a legitimate registered user attempting to extract more value than entitled to. Examined all flows: registration, wallet, payments, entitlements, generations, pricing, referrals, file access, and sharing.

---

## BL-01: Generation can be started without payment check

| Field | Value |
||---|
| **Entity** | Generation / Payment |
| **Severity** | 🔴 CRITICAL |
| **Type** | Business logic bypass |
| **Status** | ✅ FIXED |

**Attack Scenario:**

1. User registers (receives `welcome_generation` entitlement)
2. User creates a project via the frontend
3. User calls `POST /generations/projects/{project_id}` directly (bypassing frontend payment check)
4. `GenerationService.start_generation()` creates a GenerationJob without checking if payment was made
5. No payment required — generation runs anyway

**Precondition:**
- Authenticated user
- A project exists (even in draft state)

**Previous Behavior:**
- `GenerationService.start_generation()` only checked project ownership and active generation status
- **Did NOT check:** payment status, entitlement availability, or `project.price_rub > 0`

**Fixed Behavior:**
- `_verify_payment_or_entitlement()` added — checks:
  1. If `project.price_rub > 0`: verifies a `paid` Payment record exists OR `project.paid_rub > 0`
  2. If `project.price_rub == 0`: checks for available `welcome_generation` entitlement and atomically consumes it
- After consuming an entitlement, `project.paid_rub` is set to lock in the "paid" state

**Impact:**
- Unlimited free generations without payment
- Revenue loss

**Fix:** Added `_verify_payment_or_entitlement()` in `GenerationService.start_generation()` (`backend/app/services/generations/service.py:38`)

**Test:**
- `test_generation_without_payment_or_entitlement_rejected` — verifies generation is rejected when no payment/entitlement
- `test_generation_with_paid_project_allowed` — verifies paid projects work
- `test_generation_with_paid_payment_record_allowed` — verifies payment record lookup
- `test_entitlement_consumed_once` — verifies entitlement is consumed and not reusable

---

## BL-02: Welcome entitlement consumed only once (race condition fix)

| Field | Value |
||---|
| **Entity** | Entitlement / Generation |
| **Severity** | 🔴 CRITICAL |
| **Type** | Race condition — double spend |
| **Status** | ✅ FIXED |

**Attack Scenario:**

1. User has `welcome_generation` entitlement (quantity=1, consumed=0)
2. Two concurrent `POST /generations/projects/{id}` requests
3. Both check entitlement availability → both see consumed=0
4. Both create generations and consume the entitlement
5. Entitlement is consumed twice — infinite free generations

**Precondition:**
- User has a `welcome_generation` entitlement
- Two concurrent generation requests

**Previous Behavior:**
- No atomicity in entitlement consumption during generation start
- Entitlement was never consumed when generation started (only via external `consume` endpoint)

**Fixed Behavior:**
- `_consume_entitlement()` uses `EntitlementRepository.consume()` which performs an atomic `UPDATE ... WHERE consumed + quantity <= quantity SET consumed = consumed + quantity`
- The `UPDATE` is atomic at the SQL level — only one of two concurrent requests succeeds

**Impact:**
- One-time welcome entitlement could be used indefinitely

**Fix:** Linked entitlement consumption to `GenerationService.start_generation()` via atomic UPDATE

**Test:**
- `test_entitlement_consumed_once` — verifies second generation with same entitlement is rejected

---

## BL-03: Wallet debit race condition

| Field | Value |
||---|
| **Entity** | Wallet / Payment |
| **Severity** | 🔴 HIGH |
| **Type** | Race condition — double spend |
| **Status** | ✅ FIXED |

**Attack Scenario:**
```
User has balance = 100 RUB

Request A: check balance = 100 → proceeds to debit
Request B: check balance = 100 → proceeds to debit (before A commits)

Request A: balance = 100 - 100 = 0
Request B: balance = 100 - 100 = 0  (should fail, but doesn't)
```

**Precondition:**
- User has wallet balance
- Two concurrent debit requests

**Previous Behavior:**
```python
wallet = await self.get_or_create_wallet(user_id)
if (wallet.balance_rub or 0) < amount:
    raise ValidationException("Insufficient funds")
wallet.balance_rub = (wallet.balance_rub or 0) - amount
await self.db.commit()
```
- Read-modify-write pattern without `SELECT FOR UPDATE` or atomic `UPDATE`
- Under PostgreSQL with concurrent requests, both can pass the balance check before either commits

**Fixed Behavior:**
```python
result = await self.db.execute(
    Wallet.__table__.update()
    .where(Wallet.user_id == user_id, Wallet.balance_rub >= amount)
    .values(balance_rub=Wallet.balance_rub - amount)
    .returning(Wallet)
)
updated = result.one_or_none()
if updated is None:
    raise ValidationException("Недостаточно средств на кошельке")
```
- Single atomic `UPDATE ... WHERE balance_rub >= amount SET balance_rub = balance_rub - amount`
- If no rows updated, the debit failed — either insufficient funds or race lost

**Impact:**
- Users can overspend their wallet balance
- Negative balance means free unlimited spending

**Fix:** Atomic UPDATE in `WalletService.debit()` (`backend/app/services/payments/service.py:131`)

**Test:**
- `test_debit_atomic_no_overdraft` — verifies second debit fails when balance is exhausted

---

## BL-04: Webhook replay → double wallet credit (idempotency)

| Field | Value |
||---|
| **Entity** | Payment / Wallet |
| **Severity** | 🔴 HIGH |
| **Type** | Idempotency bypass |
| **Status** | ✅ FIXED |

**Attack Scenario:**
1. User pays 590 RUB via YooKassa
2. YooKassa sends webhook → handler credits wallet 590 RUB
3. Network glitch — YooKassa retries the same webhook
4. Handler processes it again → wallet credited another 590 RUB
5. User now has 1180 RUB from a 590 RUB payment

**Precondition:**
- User has made at least one successful payment
- YooKassa retries the webhook (documented YooKassa behavior)

**Previous Behavior:**
- `PaymentService.handle_webhook()` did NOT check if payment was already `status="paid"` before crediting

**Current Behavior (Fixed):**
- `if payment.status != "paid"` guard prevents re-crediting
- `PaymentService.handle_webhook()` (`backend/app/services/payments/service.py:210`)

**Impact:** Users can get unlimited wallet credit by replaying webhooks.

**Test:**
- `test_webhook_idempotency` — verifies two identical webhook calls only credit once

---

## BL-05: Promo code usage race condition

| Field | Value |
||---|
| **Entity** | PromoCode |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Race condition |
| **Status** | ✅ FIXED |

**Attack Scenario:**
```
Promo code with max_uses=1, used_count=0

Request A: validate → used_count=0 < 1 ✓
Request B: validate → used_count=0 < 1 ✓ (before A commits)

Request A: increment_promo_usage → used_count=1
Request B: increment_promo_usage → used_count=2 (should fail)
```

**Precondition:**
- Promo code with limited uses
- Concurrent requests

**Previous Behavior:**
- `PricingRepository.get_promo_code()` checks `used_count >= max_uses` (read)
- `PricingRepository.increment_promo_usage()` does `UPDATE SET used_count = used_count + 1` (write) — no constraint check
- Read and write are separate operations — TOCTOU race

**Fixed Behavior:**
```python
async def increment_promo_usage(self, promo_id: UUID, max_uses: int | None = None) -> bool:
    stmt = sa_update(PromoCode).where(PromoCode.id == promo_id)
    if max_uses is not None:
        stmt = stmt.where(PromoCode.used_count < max_uses)  # Atomic constraint
    stmt = stmt.values(used_count=PromoCode.used_count + 1).returning(PromoCode.id)
    result = await self.db.execute(stmt)
    return result.one_or_none() is not None
```
- `UPDATE ... WHERE used_count < max_uses SET used_count = used_count + 1` is atomic
- If no rows affected, the promo was exhausted — caller handles gracefully

**Impact:**
- Promo code can be used more times than `max_uses`
- Revenue loss from unlimited discounts

**Fix:** Atomic UPDATE in `PricingRepository.increment_promo_usage()` (`backend/app/repositories/pricing.py:59`)

---

## BL-06: Referral code uses_count race condition

| Field | Value |
||---|
| **Entity** | ReferralCode |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Race condition |
| **Status** | ✅ FIXED |

**Attack Scenario:**
```
Referral code with max_uses=1, uses_count=0

Request A: apply_code → reads uses_count=0 < 1 ✓
Request B: apply_code → reads uses_count=0 < 1 ✓ (before A commits)

Request A: uses_count += 1 → 1
Request B: uses_count += 1 → 2 (should fail)
```

**Precondition:**
- Referral code with limited uses
- Concurrent `apply_code` calls

**Previous Behavior:**
- `ReferralService.apply_code()` reads `code.uses_count` and `code.max_uses` in Python
- Increments: `code.uses_count += 1` in Python
- TOCTOU race between check and increment

**Fixed Behavior:**
- `ReferralRepository.increment_code_uses()` performs atomic `UPDATE ... WHERE uses_count < max_uses SET uses_count = uses_count + 1`
- If no rows affected, the code is exhausted — rollback and raise `ValidationException`

**Impact:** Referral codes can be used beyond their limit.

**Fix:** Added `increment_code_uses()` method, updated `apply_code()` (`backend/app/services/referrals/service.py:47`)

---

## BL-07: Referral bonus double-grant race condition

| Field | Value |
||---|
| **Entity** | Referral |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Race condition |
| **Status** | ✅ FIXED |

**Attack Scenario:**
```
Referral with status="pending", referrer_bonus_granted=False

Request A: mark_referral_completed → reads status="pending", grants bonus, sets granted=True
Request B: mark_referral_completed → reads status="pending" (before A commits), grants bonus again

Both requests grant referrer_bonus — double payout
```

**Precondition:**
- A referral is in "pending" status
- Two concurrent webhook deliveries for the same payment

**Previous Behavior:**
- Read referral → check status → grant bonus → set `referrer_bonus_granted = True` → commit
- TOCTOU race between status check and commit

**Fixed Behavior:**
- Uses atomic `UPDATE ... WHERE status="pending" SET status="completed", referrer_bonus_granted=True, referee_bonus_granted=True`
- If no rows affected, referral was already completed — return `None` without granting bonus

**Impact:** Referrer/referee bonuses granted multiple times for same payment.

**Fix:** Atomic UPDATE in `mark_referral_completed()` (`backend/app/services/referrals/service.py:75`)

---

## BL-08: force_regenerate bypasses active generation check

| Field | Value |
||---|
| **Entity** | Generation |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Business logic bypass |
| **Status** | ✅ FIXED |

**Attack Scenario:**
1. User starts a generation for a project
2. Generation is `status="processing"`
3. User calls `POST /generations/projects/{project_id}` with `force_regenerate: true`
4. A NEW generation is created, running alongside the existing one
5. Both jobs consume resources — double billing on usage-based pricing

**Precondition:**
- User has an active generation
- User can set `force_regenerate: true`

**Previous Behavior:**
- `force_regenerate: true` simply skipped the conflict check — both generations run

**Fixed Behavior:**
- When `force_regenerate` is true and an active generation exists, the existing one is cancelled first
- `existing.status = "cancelled"` before creating the new generation

**Impact:**
- Concurrent generations on same project — resource waste
- Potential billing confusion

**Fix:** Cancel existing generation before creating new one (`backend/app/services/generations/service.py:30-34`)

**Test:**
- `test_force_regenerate_cancels_existing` — verifies first generation is cancelled

---

## BL-09: Bonus balance used for payment

| Field | Value |
||---|
| **Entity** | Wallet / Payment |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Missing feature |
| **Status** | ✅ FIXED |

**Attack Scenario:**

1. User has 0 RUB balance and 500 RUB bonus balance
2. User calls `/pricing/calculate` → sees `total_rub: 590`
3. User pays 590 RUB via YooKassa
4. Bonus balance is never checked or applied

**Precondition:**
- User has bonus balance
- User makes real payment

**Previous Behavior:**
- `PaymentService.create_payment()` did not check for or apply bonus balance

**Fixed Behavior:**
- `POST /payments/projects/{id}` now checks wallet bonus balance before creating payment
- If bonus covers full amount, `project.paid_rub` is set and a 0-RUB payment is created (no external charge)
- If bonus covers partial amount, only the remaining balance is charged via YooKassa
- Bonus debit is atomic via `debit_bonus()` using `UPDATE ... WHERE bonus_balance >= amount`
- Race condition handled: if `debit_bonus` fails (insufficient bonus), falls back to full amount via YooKassa

**Impact:**
- Users were paying real money when they had bonus balance available

**Fix:** Bonus balance deduction added to payment creation flow (`backend/app/api/v1/payments.py:47-68`)

---

## BL-10: No email verification → multiple account creation

| Field | Value |
||---|
| **Entity** | Account |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Business logic bypass |
| **Status** | ⚠️ PENDING |

**Attack Scenario:**

1. Register account A → get `welcome_generation` free entitlement
2. Register account B with different email → get another free entitlement
3. Repeat indefinitely → unlimited free generations

**Precondition:**
- No email verification (confirmed in auth audit)
- Welcome entitlement per account

**Current Behavior:**
- Registration is completely open — no CAPTCHA, no email verification
- Each new account gets a `welcome_generation` entitlement
- IP-based rate limiting exists but is easily bypassed with cloud instances

**Expected Behavior:**
- Email verification required before entitlement is granted
- Or: detect and flag multiple accounts from same IP/device

**Impact:**
- Unlimited free content generation
- Bypass of paid features

**Fix:** Require email verification before granting welcome entitlement. Track `registration_ip` on user and limit one welcome entitlement per IP.

---

## BL-11: Presigned URL exposure in share links

| Field | Value |
||---|
| **Entity** | Files / Storage |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Information exposure |
| **Status** | ⚠️ PENDING |

**Attack Scenario:**

1. User creates a share link for their project
2. Share link returns `video_url` — a presigned URL to S3/MinIO storage
3. User copies the presigned URL and shares it directly (bypassing the share token)
4. The presigned URL is accessible by anyone until it expires (1 hour)

**Precondition:**
- User has a completed generation with a share link
- User can view the share page

**Current Behavior:**
- `get_public_share()` returns `generation.output_json["video_url"]` directly
- Presigned URLs have 1-hour expiry but are valid from anywhere
- No access logging or revocation

**Expected Behavior:**
- Serve videos through a proxy endpoint that checks the share token
- Or: shorten presigned URL expiry and regenerate on each request
- Or: use signed URLs with IP binding

**Impact:**
- Share link URLs can be distributed, bypassing view limits
- Videos can be downloaded and re-shared indefinitely within the 1-hour window

**Fix:** Replace direct presigned URLs with a proxy endpoint, or implement URL revocation.

---

## BL-12: Payment creation can use any user's project (no cross-user payment)

| Field | Value |
||---|
| **Entity** | Payment / Project |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Business logic bypass |
| **Status** | ✅ VERIFIED SAFE |

**Attack Scenario:**

1. User A creates a project and gets a share link
2. User B calls `POST /payments/projects/{A_project_id}` — but `ProjectRepository.get_by_id(project_id, user_id)` checks ownership
3. This is safe — the payment endpoint verifies the project belongs to the user

**Verified:** Safe — ownership check in `backend/app/api/v1/payments.py:39`

---

## BL-13: Refund does not revoke entitlement or generation access

| Field | Value |
||---|
| **Entity** | Payment / Generation |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Revenue leakage |
| **Status** | ⚠️ PENDING (no refund endpoint exists) |

**Attack Scenario:**

1. User pays 590 RUB → generation starts and completes
2. User calls YooKassa refund API directly (or support refunds)
3. Refund webhook arrives → wallet debited 590 RUB
4. But user keeps the generated video — service already delivered

**Precondition:**
- User has completed a generation
- Refund is processed (manually or via support)

**Current Behavior:**
- No refund webhook handler exists (`payment.refund` event not handled)
- No mechanism to revoke access after refund
- `refunded_at` field exists on Payment model but is never set

**Expected Behavior:**
- Handle `refund.succeeded` webhook
- Mark payment as `refunded`
- Optionally revoke share links or mark generation as inaccessible
- Deduct refund from wallet balance

**Impact:**
- Users can get refunds and keep the service
- Revenue loss

**Fix:** Add refund webhook handler, implement access revocation.

---

## BL-14: Double payment on same project prevented

| Field | Value |
||---|
| **Entity** | Payment / Pricing |
| **Severity** | ⚠️ MEDIUM |
| **Type** | Business logic bypass |
| **Status** | ✅ FIXED |

**Attack Scenario:**

1. User calls `/pricing/calculate` → sets `project.price_rub = 590`
2. User calls `POST /payments/projects/{id}` → creates payment for 590 RUB
3. User calls `/pricing/calculate` again with different params → `project.price_rub` changes
4. User calls `POST /payments/projects/{id}` again → creates a second payment

**Precondition:**
- Project exists
- User can calculate price multiple times

**Previous Behavior:**
- No check prevented creating multiple payments on the same project
- `project.paid_rub` was not set during payment creation

**Fixed Behavior:**
- `POST /payments/projects/{id}` now checks:
  1. `project.paid_rub > 0` → reject with `ConflictException`
  2. Existing `paid` Payment record for this project → reject with `ConflictException`
- When payment is fully covered by bonus, `project.paid_rub` is set immediately
- After YooKassa webhook fires, the payment is marked as `paid`

**Impact:**
- Double payment on same project
- Price manipulation via repeated /pricing/calculate calls

**Fix:** Added payment existence checks in `POST /payments/projects/{id}` (`backend/app/api/v1/payments.py:43-46`)

---

## Summary

| ID | Issue | Severity | Status |
|---|---|---|---|
| BL-01 | Generation without payment check | 🔴 CRITICAL | ✅ FIXED |
| BL-02 | Welcome entitlement double spend (race) | 🔴 CRITICAL | ✅ FIXED |
| BL-03 | Wallet debit race condition | 🔴 HIGH | ✅ FIXED |
| BL-04 | Webhook replay double-credit | 🔴 HIGH | ✅ FIXED |
| BL-05 | Promo code usage race | ⚠️ MEDIUM | ✅ FIXED |
| BL-06 | Referral code uses_count race | ⚠️ MEDIUM | ✅ FIXED |
| BL-07 | Referral bonus double-grant race | ⚠️ MEDIUM | ✅ FIXED |
| BL-08 | force_regenerate bypasses conflict check | ⚠️ MEDIUM | ✅ FIXED |
| BL-09 | Bonus balance not used for payment | ⚠️ MEDIUM | ✅ FIXED |
| BL-10 | Multiple account creation | ⚠️ MEDIUM | ⚠️ PENDING |
| BL-11 | Presigned URL exposure in share links | ⚠️ MEDIUM | ⚠️ PENDING |
| BL-12 | Cross-user payment | Safe | ✅ VERIFIED |
| BL-13 | No refund handling | ⚠️ MEDIUM | ⚠️ PENDING |
| BL-14 | Mutable project price_rub | ⚠️ MEDIUM | ✅ FIXED |

### Files Modified

- `backend/app/services/generations/service.py` — added payment/entitlement verification before generation start
- `backend/app/services/payments/service.py` — atomic wallet debit
- `backend/app/services/referrals/service.py` — atomic referral completion, atomic code usage increment
- `backend/app/repositories/pricing.py` — atomic promo code usage increment
- `backend/app/repositories/referrals.py` — added `increment_code_uses()` atomic method
- `backend/app/repositories/entitlements.py` — fixed consume return check for SQLite compatibility
- `backend/tests/test_generations.py` — added payment/entitlement verification tests
- `backend/tests/test_payments.py` — added webhook idempotency and wallet debit tests