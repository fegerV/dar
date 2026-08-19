# DarAgent Backend — Red Team Security Audit Report (SECOND PASS)

## Executive Summary

**Scope:** `backend/app/api/v1/`, `backend/app/services/`, `backend/app/middleware/`  
**Auditor:** Independent Red Team Security Engineer  
**Date:** 2026-08-19  
**RED TEAM SCORE: 65 / 100**

The first-pass audit identified 20 attack vectors (ATTACK-01 through ATTACK-20).  
In response, the following have been FIXED in production code:

- ATTACK-01 (Fake promo codes) — FIXED: database-backed PromoCode validation
- ATTACK-04 (XSS in email) — FIXED: html.escape + URL scheme validation
- ATTACK-05 (CSRF bypass) — FIXED: CSRF extended to all mutating endpoints
- ATTACK-06 (Entitlement race condition) — FIXED: atomic UPDATE with WHERE clause
- ATTACK-09 (IDOR in prompt compiler) — FIXED: ownership check with user_id
- ATTACK-15 (Mock payment mode) — FIXED: startup guard in production
- ATTACK-16 (Audit log silent bypass) — FIXED: log level upgraded to warning
- ATTACK-19 (Missing security headers) — FIXED: SecurityHeadersMiddleware added
- ATTACK-20 (Contact import validation) — FIXED: input validation, length limits

The second-pass audit identified 5 new vulnerabilities and 11 previously known issues remain open:

**New vulnerabilities (second pass):**

- RT2-01: IDOR in Recommendation `select` — ownership check was after data modification
- RT2-02: Path traversal in asset upload filename
- RT2-03: IDOR in asset confirmation (`object_key` from user input)
- RT2-04: Analytics event spoofing (arbitrary event names + unverified project_id)
- RT2-05: Unrestricted feature flag setting

All new vulnerabilities have been FIXED in this pass.

**Remaining open issues:**

- ATTACK-02 (IDOR in preflight) — FIXED (added user_id ownership check)
- ATTACK-03 (IDOR in recipe access) — FIXED (admin-only access)
- ATTACK-08 (Hardcoded default secrets) — PARTIALLY MITIGATED (production guard exists, defaults still in dev)
- ATTACK-11 (Admin/is_admin desync) — OPEN
- ATTACK-12 (Telegram link without verification) — OPEN
- ATTACK-13 (SSRF via image_url) — OPEN
- ATTACK-14 (Analytics spoofing, partially fixed) — PARTIALLY FIXED
- ATTACK-17 (Admin impersonation without MFA) — OPEN
- ATTACK-18 (Weak rate limiting) — OPEN

---

## Second-Pass Vulnerability Catalog

### RT2-01: IDOR in Recommendation `select` (Authorization After Action)
- **STATUS:** FIXED
- **SEVERITY:** HIGH
- **PRECONDITION:** Authenticated user
- **CODE EVIDENCE:** `backend/app/services/recommendations/service.py:111-138` (original) — `select()` called `repo.get_by_id()` and `repo.mark_selected()` BEFORE `project_repo.get_by_id(project_id, user_id)`.
- **ATTACK STEPS:**
  1. Attacker obtains a victim's `project_id` and `recommendation_id`.
  2. Attacker calls `POST /api/v1/recommendations/projects/{victim_project_id}/select/{victim_recommendation_id}`.
  3. The recommendation is marked as "selected" (data modified) before ownership is verified.
  4. Although the API returns 404 (ownership check fails after modification), the database was already modified.
- **EXPECTED RESULT:** Ownership check should occur BEFORE any data modification.
- **ACTUAL RESULT (pre-fix):** Data was modified before the authorization check.
- **IMPACT:** An attacker can corrupt recommendation analytics and rankings for other users' projects.
- **RECOMMENDED FIX:** Move `project_repo.get_by_id(project_id, user_id)` to the top of `select()`, before any `repo` calls.
- **REGRESSION TEST:** Submit a select request for another user's project; expect 404 with no database changes.

### RT2-02: Path Traversal in Asset Upload Filename
- **STATUS:** FIXED
- **SEVERITY:** HIGH
- **PRECONDITION:** Authenticated user
- **CODE EVIDENCE:** `backend/app/services/assets/service.py:21` (original) — `object_key = f"uploads/{user_id}/{asset_id}_{body.filename}"`. `body.filename` was used directly without sanitization.
- **ATTACK STEPS:**
  1. Attacker calls `POST /api/v1/assets/upload-url` with `filename = "../../../etc/cron.d/exploit"`.
  2. The generated presigned URL allows uploading to an arbitrary path in storage.
  3. If the storage bucket has path-based access policies, the attacker could overwrite critical files.
- **EXPECTED RESULT:** Filenames should be sanitized with `os.path.basename()` and file extensions should be validated.
- **ACTUAL RESULT (pre-fix):** Arbitrary path traversal in object key names.
- **IMPACT:** Overwriting critical storage objects, potential RCE via uploaded executable files.
- **RECOMMENDED FIX:** Sanitize with `os.path.basename()`, validate against an allowlist of extensions.
- **REGRESSION TEST:** Attempt upload with `filename = "../../test.txt"`; expect ValidationException or sanitized path.

### RT2-03: IDOR in Asset Confirmation (object_key Manipulation)
- **STATUS:** FIXED
- **SEVERITY:** HIGH
- **PRECONDITION:** Authenticated user
- **CODE EVIDENCE:** `backend/app/services/assets/service.py:30-46` (original) — `confirm_upload()` accepts `object_key` from user input and creates a `StorageObject` record without verifying the key belongs to the user.
- **ATTACK STEPS:**
  1. Attacker obtains a legitimate `asset_id` (via enumeration or from a victim's upload).
  2. Attacker calls `POST /api/v1/assets/confirm-upload?asset_id=<victim's>&object_key=<victim's_object_key>`.
  3. A new `StorageObject` and `Asset` record is created linking the victim's storage object to the attacker's user.
  4. The attacker can now access the victim's uploaded file via `GET /api/v1/assets/{asset_id}`.
- **EXPECTED RESULT:** `object_key` should be validated to start with `uploads/{user_id}/` and `asset_id` should be checked for existing ownership.
- **ACTUAL RESULT (pre-fix):** Any user could reference any storage object.
- **IMPACT:** Unauthorized access to other users' uploaded files (photos, videos, documents).
- **RECOMMENDED FIX:** Verify `object_key.startswith(f"uploads/{user_id}/")` and check existing asset ownership.
- **REGRESSION TEST:** Confirm-upload with another user's `object_key`; expect 404.

### RT2-04: Analytics Event Spoofing & Unverified Project Association
- **STATUS:** FIXED
- **SEVERITY:** MEDIUM
- **PRECONDITION:** Authenticated user
- **CODE EVIDENCE:** `backend/app/api/v1/analytics.py:14-29` (original) — `track_event` accepts arbitrary `event_name` and `project_id` without validation.
- **ATTACK STEPS:**
  1. Attacker calls `POST /api/v1/analytics/events?event_name=arbitrary_event&project_id=<victim's>`.
  2. The server logs the event against the victim's project without verifying ownership.
  3. Attacker can flood the analytics table with arbitrary event names.
  4. Attacker can inject false funnel data for other users' projects.
- **EXPECTED RESULT:** Event names should be whitelisted; project_id should be ownership-verified.
- **ACTUAL RESULT (pre-fix):** Any event name accepted; any project_id associated without check.
- **IMPACT:** Funnel data corruption, false business metrics, database flooding (DoS).
- **RECOMMENDED FIX:** Whitelist event names; verify project ownership before associating events.
- **REGRESSION TEST:** Submit event with invalid name; expect ValidationException. Submit with another user's project_id; expect 404.

### RT2-05: Unrestricted Feature Flag Setting
- **STATUS:** FIXED
- **SEVERITY:** MEDIUM
- **PRECONDITION:** Authenticated user
- **CODE EVIDENCE:** `backend/app/api/v1/analytics.py:81-90` (original) — `set_feature_flag` accepts arbitrary `flag_name` from URL path.
- **ATTACK STEPS:**
  1. Attacker calls `POST /api/v1/analytics/feature-flags/premium_features?enabled=true`.
  2. The flag `premium_features` is set for the attacker's user.
  3. If any code checks for this flag, the attacker gains access to premium features.
- **EXPECTED RESULT:** Feature flag names should be validated against an allowlist.
- **ACTUAL RESULT (pre-fix):** Arbitrary flag names accepted.
- **IMPACT:** Privilege escalation via feature flag manipulation.
- **RECOMMENDED FIX:** Whitelist allowed feature flag names.
- **REGRESSION TEST:** Set feature flag with arbitrary name; expect ValidationException.

---

## Previously Identified Vulnerabilities — Status

| Attack ID | Vulnerability | Previous Status | Current Status |
|-----------|--------------|------|---------------|
| ATTACK-01 | Payment Bypass (Fake Promo) | CONFIRMED | **FIXED** |
| ATTACK-02 | IDOR in Preflight | CONFIRMED | **FIXED** |
| ATTACK-03 | IDOR in Recipes | CONFIRMED | **FIXED** (admin-only) |
| ATTACK-04 | XSS in Email | CONFIRMED | **FIXED** |
| ATTACK-05 | CSRF Bypass | CONFIRMED | **FIXED** |
| ATTACK-06 | Race Condition (Entitlement) | CONFIRMED | **FIXED** |
| ATTACK-07 | IDOR in Feedback | CONFIRMED | FIXED (from IDOR audit) |
| ATTACK-08 | Hardcoded Secrets | CONFIRMED | **PARTIALLY MITIGATED** |
| ATTACK-09 | IDOR in Prompt Compiler | CONFIRMED | **FIXED** |
| ATTACK-10 | Unauthenticated Templates | CONFIRMED | FIXED (render now requires auth) |
| ATTACK-11 | Admin/is_admin Desync | CONFIRMED | **OPEN** |
| ATTACK-12 | Telegram Without Verification | CONFIRMED | **OPEN** |
| ATTACK-13 | SSRF via image_url | CONFIRMED | **OPEN** |
| ATTACK-14 | Analytics Spoofing | CONFIRMED | **PARTIALLY FIXED** |
| ATTACK-15 | Mock Payment Mode | CONFIRMED | **FIXED** |
| ATTACK-16 | Audit Log Bypass | CONFIRMED | **FIXED** |
| ATTACK-17 | Admin Impersonation | CONFIRMED | **OPEN** |
| ATTACK-18 | Weak Rate Limiting | CONFIRMED | **OPEN** |
| ATTACK-19 | Missing Security Headers | CONFIRMED | **FIXED** |
| ATTACK-20 | Contact Import Validation | CONFIRMED | **FIXED** |

---

## Remaining Open Issues (Detailed)

### ATTACK-08 (Remaining): Hardcoded Default Secrets
- **SEVERITY:** HIGH (in dev mode)
- **STATUS:** PARTIALLY MITIGATED — production guard added, but defaults remain in source.
- **RECOMMENDED FIX:** Generate random secrets on first run; fail to start in any environment if secrets match defaults.

### ATTACK-11 (Remaining): Admin/is_admin Desync
- **SEVERITY:** MEDIUM
- **STATUS:** OPEN
- **CODE EVIDENCE:** `backend/app/models/user.py:25` — `is_admin: Mapped[bool]` column exists on User model. `backend/app/services/admin/service.py:41-61` — `AdminUser` table is separate from `User.is_admin`.
- **IMPACT:** If any code sets `User.is_admin = True` without creating an `AdminUser` record, or vice versa, the authorization model is inconsistent.
- **RECOMMENDED FIX:** Remove `User.is_admin` and rely solely on `AdminUser` table, or synchronize both in `ensure_single_admin`.

### ATTACK-12 (Remaining): Telegram Account Linking Without Verification
- **SEVERITY:** MEDIUM
- **STATUS:** OPEN
- **CODE EVIDENCE:** `backend/app/api/v1/telegram.py:20-40` — `link_telegram` endpoint sets `user.telegram_user_id = body.telegram_id` with no verification.
- **IMPACT:** Attacker can link any Telegram ID (including a victim's) to their account, intercepting scheduled deliveries.
- **RECOMMENDED FIX:** Implement Telegram OAuth or a confirmation code flow.

### ATTACK-13 (Remaining): SSRF via Unvalidated image_url
- **SEVERITY:** MEDIUM
- **STATUS:** OPEN
- **CODE EVIDENCE:** `backend/app/api/v1/intelligence.py:34` — `image_url` is stored and passed to workers/AI providers. `backend/app/services/intelligence/preflight.py:16` — accepts arbitrary `image_url`.
- **IMPACT:** If any worker process fetches `image_url`, attacker can target internal services (e.g., `http://169.254.169.254/`, `http://localhost:6379/`).
- **RECOMMENDED FIX:** Validate URL scheme (https only), block private IP ranges, use egress proxy.

### ATTACK-17 (Remaining): Admin Impersonation Without MFA
- **SEVERITY:** MEDIUM
- **STATUS:** OPEN
- **CODE EVIDENCE:** `backend/app/api/v1/admin.py:220-239` — `impersonate_user` immediately returns valid tokens for any user.
- **IMPACT:** If admin account is compromised, attacker gains instant access to any user account.
- **RECOMMENDED FIX:** Require re-authentication or TOTP for impersonation.

### ATTACK-18 (Remaining): Weak Rate Limiting
- **SEVERITY:** LOW-MEDIUM
- **STATUS:** OPEN
- **CODE EVIDENCE:** `backend/app/middleware/rate_limit.py:31-58` — IP-based only, no user context, in-memory fallback doesn't work across workers.
- **IMPACT:** Brute force attacks at 120 req/min per IP, rate limit bypass via NAT/CDN.
- **RECOMMENDED FIX:** Add user-ID-based rate limiting; ensure Redis is required in production.

---

## Updated Risk Matrix

| Attack ID | Vulnerability | Severity | Status |
|-----------|--------------|----------|--------|
| ATTACK-01 | Payment Bypass (Fake Promo) | CRITICAL | FIXED |
| ATTACK-02 | IDOR in Preflight | HIGH | FIXED |
| ATTACK-03 | IDOR in Recipes | HIGH | FIXED |
| ATTACK-04 | XSS in Email | HIGH | FIXED |
| ATTACK-05 | CSRF Bypass | HIGH | FIXED |
| ATTACK-06 | Race Condition (Entitlement) | MEDIUM-HIGH | FIXED |
| ATTACK-07 | IDOR in Feedback | MEDIUM-HIGH | FIXED |
| ATTACK-08 | Hardcoded Secrets | HIGH | PARTIALLY MIT |
| ATTACK-09 | IDOR in Prompt Compiler | MEDIUM-HIGH | FIXED |
| ATTACK-10 | Unauthenticated Templates | MEDIUM | FIXED |
| ATTACK-11 | Admin/is_admin Desync | MEDIUM | OPEN |
| ATTACK-12 | Telegram Without Verification | MEDIUM | OPEN |
| ATTACK-13 | SSRF via image_url | MEDIUM | OPEN |
| ATTACK-14 | Analytics Spoofing | MEDIUM | PARTIALLY FIXED |
| ATTACK-15 | Mock Payment Mode | MEDIUM | FIXED |
| ATTACK-16 | Audit Log Bypass | MEDIUM | FIXED |
| ATTACK-17 | Admin Impersonation | MEDIUM | OPEN |
| ATTACK-18 | Weak Rate Limiting | LOW-MEDIUM | OPEN |
| ATTACK-19 | Missing Security Headers | LOW-MEDIUM | FIXED |
| ATTACK-20 | Contact Import Validation | LOW-MEDIUM | FIXED |
| RT2-01 | IDOR in Recommendation Select | HIGH | FIXED |
| RT2-02 | Path Traversal in Asset Upload | HIGH | FIXED |
| RT2-03 | IDOR in Asset Confirmation | HIGH | FIXED |
| RT2-04 | Analytics Event Spoofing | MEDIUM | FIXED |
| RT2-05 | Unrestricted Feature Flags | MEDIUM | FIXED |

---

## Updated Top 10 Attack Paths (Post-Remediation)

1. **Admin Takeover via Hardcoded JWT Secret (ATTACK-08):** Default `JWT_SECRET_KEY = "change-me-jwt"` → Forge admin JWT → Access `/admin/impersonate` → Take over any user → Access all data and wallets.
2. **SSRF via Preflight Image URL (ATTACK-13):** POST `/intelligence/preflight` with `image_url=http://169.254.169.254/` → Worker fetches internal URL → Cloud credential exfiltration.
3. **Storage Takeover via Default MinIO Creds (ATTACK-08):** Access MinIO with `minioadmin/minioadmin` → Read all user assets → Overwrite/delete objects.
4. **Telegram Delivery Hijack (ATTACK-12):** Link victim's Telegram ID via `/telegram/link` → Receive victim's scheduled deliveries.
5. **Admin Privilege Escalation via is_admin Desync (ATTACK-11):** Direct DB `UPDATE users SET is_admin = true` (if SQLi/DB access exists) → Access admin endpoints without AdminUser record.
6. **Admin Account Compromise → Impersonation (ATTACK-17):** Compromise admin credential → `POST /admin/users/{id}/impersonate` → Get valid tokens for any user → Full account takeover.
7. **Analytics Poisoning + Rate Limit Bypass (ATTACK-14 + ATTACK-18):** Flood `/analytics/events` with spoofed data at 120 req/min → Corrupt funnel metrics → Skew A/B test results → Misinform product decisions.
8. **Brute Force Password Attack (ATTACK-18):** Use `/auth/login` at 120 req/min per IP → Crack weak passwords via credential stuffing.
9. **Unvalidated Contact Import DoS (ATTACK-20, partially fixed):** Import 10,000 contacts → Database bloat → Degrade query performance.
10. **Audit Log Evasion (ATTACK-16, fixed → but still has partial risk):** Craft malformed request that triggers exception in audit path → Request still processed but not logged → Attack goes undetected.

---

## Overall Security Posture

**RED TEAM SCORE: 65 / 100**

The score reflects:
- **8 critical/high vulnerabilities FIXED** in the first pass (promo codes, CSRF, race condition, prompt compiler IDOR, XSS, mock payment, audit logs, security headers).
- **5 high/medium vulnerabilities FIXED** in the second pass (recommendation IDOR, path traversal, asset confirmation IDOR, analytics spoofing, feature flag abuse).
- **Remaining risks:** Hardcoded secrets in dev mode, Telegram link verification, SSRF via image_url, admin is_admin desync, admin impersonation without MFA, weak rate limiting.

These remaining issues are lower exploitability (require dev/staging access or admin compromise) but should still be addressed before production deployment.
