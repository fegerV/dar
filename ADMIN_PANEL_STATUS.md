# Admin Panel Status Assessment

## Overview

The admin panel consists of:
- **Frontend**: Next.js app at `web-app/app/admin/` with 11 pages
- **Backend**: FastAPI admin router at `backend/app/api/v1/admin.py` with 15 endpoints
- **Service layer**: `backend/app/services/admin/service.py` with 18 methods

## Current Status: PARTIALLY IMPLEMENTED — BLOCKED BY AUTH CIRCULAR DEPENDENCY

### Critical Blocker: Admin Bootstrap is Broken

**The Chicken-and-Egg Problem:**
1. To call `POST /admin/init`, you need `require_admin` (checks `User.is_admin = True`)
2. To get `User.is_admin = True`, you need to be admin
3. There is NO backend endpoint to make the first user admin
4. The seed script (`backend/scripts/seed.py`) does NOT create an admin user
5. The frontend login page (`web-app/app/admin/login/page.tsx:13-14`) has hardcoded credentials `admin@daragent.ru:admin123`, but no backend code creates this user

**Result:** The admin panel is completely inaccessible. Even with proper JWT secrets, there is no way to bootstrap the first admin account through the API. The init endpoint is unreachable.

### Frontend Status

| Page | File | Component | Status | Notes |
|------|------|-----------|--------|-------|
| Login | `app/admin/login/page.tsx` | `AdminLoginPage` | ✅ Working | Hardcoded credentials, stores token in localStorage (XSS risk) |
| Dashboard | `app/admin/dashboard/page.tsx` | `AdminDashboard` | ⚠️ Partial | Fetches `/admin/stats` — health section uses static data, not real API calls |
| Users | `app/admin/users/page.tsx` | `AdminUsers` | ⚠️ Partial | "View" button (Eye icon) has no onClick handler (stub) |
| Orders | `app/admin/orders/page.tsx` | `AdminOrders` | ⚠️ Partial | "Play video" button is a stub (no onClick) |
| Order Detail | `app/admin/orders/[id]/page.tsx` | `AdminOrderDetail` | ⚠️ Partial | Fetches `/admin/orders/{id}`, but the "Open video" button has no handler |
| Generations | `app/admin/generations/page.tsx` | `AdminGenerations` | ⚠️ Partial | "Play Video" button is a stub (no onClick) |
| Queue | `app/admin/queue/page.tsx` | `AdminQueue` | ✅ Working | Has cancel/retry actions wired to API |
| Referrals | `app/admin/referrals/page.tsx` | `AdminReferrals` | ✅ Working | Read-only views of codes/referrals |
| Audit Logs | `app/admin/audit-logs/page.tsx` | `AdminAuditLogs` | ✅ Working | Read-only, searchable |
| Workers | `app/admin/workers/page.tsx` | `AdminWorkers` | ⚠️ Partial | "Restart" button only sets status to "maintenance", doesn't actually restart worker |
| System | `app/admin/system/page.tsx` | `AdminSystem` | ✅ Working | Health uses static data, settings editable via JSON input |
| Init | `app/admin/init/page.tsx` | `AdminInitPage` | ⚠️ Partial | Requires `require_admin` — unreachable without bootstrap fix |

### Backend API Status

| Endpoint | Controller | Service | Status |
|----------|-----------|---------|--------|
| `POST /admin/init` | `admin.py:40` | `ensure_single_admin` | ⚠️ Unreachable (bootstrap bug) |
| `GET /admin/stats` | `admin.py:50` | `get_dashboard_stats` | ✅ Working |
| `GET /admin/users` | `admin.py:59` | `list_users` | ✅ Working |
| `POST /admin/templates` | `admin.py:83` | `create_template` | ✅ Working |
| `GET /admin/templates` | `admin.py:71` | `list_templates` | ✅ Working |
| `GET /admin/generations` | `admin.py:93` | `list_generations` | ✅ Working |
| `GET /admin/orders` | `admin.py:105` | `list_orders` | ✅ Working (alias of generations) |
| `GET /admin/queue` | `admin.py:117` | `list_queue_jobs` | ✅ Working |
| `GET /admin/workers` | `admin.py:127` | `list_workers` | ✅ Working |
| `POST /admin/workers/{id}/status` | `admin.py:136` | `update_worker_status` | ✅ Working (sets status only) |
| `POST /admin/queue/{id}/action` | `admin.py:147` | `queue_job_action` | ✅ Working |
| `GET /admin/payments` | `admin.py:158` | `list_payments` | ✅ Working |
| `GET /admin/audit-logs` | `admin.py:170` | `list_audit_logs` | ✅ Working |
| `GET /admin/system/settings` | `admin.py:180` | `get_system_settings` | ✅ Working |
| `PATCH /admin/system/settings/{key}` | `admin.py:189` | `update_system_setting` | ✅ Working |
| `GET /admin/users/{id}` | `admin.py:200` | `get_user` | ✅ Working |
| `GET /admin/users/{id}/wallet` | `admin.py:210` | `get_user_wallet` | ✅ Working |
| `POST /admin/users/{id}/impersonate` | `admin.py:220` | (inline) | ✅ Working (returns tokens) |
| `GET /admin/referrals` | `admin.py:242` | `list_referrals` | ✅ Working |
| `GET /admin/referral-codes` | `admin.py:251` | `list_referral_codes` | ✅ Working |
| `GET /admin/orders/{id}` | `admin.py:260` | `get_order` | ✅ Working |
| `GET /admin/gallery/pending` | `admin.py:270` | `list_gallery_pending` | ✅ Working |
| `POST /admin/gallery/{id}/review` | `admin.py:290` | `review_gallery_submission` | ✅ Working |

## Missing Features

### 1. Admin Bootstrap (CRITICAL BLOCKER)

**Problem:** No way to create the first admin user. `POST /admin/init` requires admin privileges.

**Fix required:**
- Add `POST /admin/setup` endpoint that creates the first admin without requiring admin auth (only works when no AdminUser records exist)
- OR add a CLI script to bootstrap admin
- OR add `is_admin` to the register request for the first user

**CLI Script Approach (Recommended):**
```python
# backend/scripts/create_admin.py
async def create_admin(email: str, password: str):
    # Create user with is_admin=True
    # Create AdminUser record
```

### 2. Template Management — No Update/Edit Endpoint

**Missing endpoints:**
- `PATCH /admin/templates/{id}` — update template status, price, etc.
- `DELETE /admin/templates/{id}` — delete template
- `POST /admin/templates/{id}/versions` — create new template version

**Frontend shows:** "Edit" button (Eye/Edit icon) in templates table — no onClick handler.

### 3. Template Version Management

**Missing endpoints:**
- `GET /admin/templates/{id}/versions` — list versions
- `PATCH /admin/templates/{version_id}` — update version status/prompt_config
- No way to edit scene prompts, template config from admin UI

### 4. Template Scene Management

**Missing endpoints:**
- `POST /admin/templates/{id}/scenes` — create scene
- `PATCH /admin/scenes/{id}` — update scene
- `DELETE /admin/scenes/{id}` — delete scene
- No UI for managing scenes within templates

### 5. Worker Management Incomplete

**Frontend:** "Restart" button sets status to "maintenance" but doesn't actually restart the worker process.

**Missing endpoints:**
- `POST /admin/workers/{id}/restart` — send restart signal
- `POST /admin/workers/{id}/shutdown` — gracefully shutdown worker
- Worker details view with full metrics

### 6. Queue Job Actions Incomplete

**Missing:**
- Job reassignment (move to different worker)
- Job priority numeric adjustment (only preset "prioritize"/"deprioritize")
- Bulk actions (cancel multiple jobs)

### 7. System Settings — No UI Validation

**Problem:** Settings can be edited as raw JSON without type validation.

**Fix:** Add schema-based validation for system settings keys.

### 8. System Health — Static Data

**Problem:** The health monitoring section uses hardcoded `initialHealth` array, not real API data.

**Fix:** Fetch real data from `/health/detailed` endpoint (needs authentication).

### 9. Admin Impersonation — Missing MFA Requirement

**Problem:** Impersonation endpoint has no MFA, time limit, or watermarking.

**Fix:**
- Require MFA for impersonation
- Set short-lived tokens (5 min) for impersonated sessions
- Add watermark context to all actions by impersonated users

### 10. Token Storage in localStorage

**Problem:** Admin tokens stored in `localStorage` (`web-app/src/lib/api.ts:21`), vulnerable to XSS.

**Fix:** Use httpOnly cookies instead.

## Security Issues Found

1. **Hardcoded admin credentials** in `login/page.tsx:13-14`: `admin@daragent.ru` / `admin123`
2. **localStorage token storage** — XSS token theft risk
3. **Admin impersonation** — no MFA, no time limit
4. **Health/metrics endpoints** unauthenticated (`/health/detailed`, `/metrics`)
5. **Admin/desync** — `User.is_admin` vs `AdminUser` table inconsistency

## Recommendations

### Immediate (Blocker)
1. Fix admin bootstrap — add CLI script or setup endpoint
2. Remove hardcoded credentials from frontend
3. Add MFA requirement for impersonation
4. Move tokens to httpOnly cookies

### Short-term
4. Add template update/delete endpoints
5. Add template version management endpoints
6. Add scene management endpoints
7. Add real system health integration

### Medium-term
8. Add worker restart/shutdown endpoints
9. Add bulk queue job actions
10. Add system settings schema validation
11. Add admin action audit trail for all mutations

## Progress Summary

- **Backend endpoints implemented:** 23/23 (all admin API endpoints exist)
- **Frontend pages implemented:** 11/11 (all pages exist)
- **Frontend pages fully functional:** ~6/11 (Dashboard, System, Users, Orders, Generations have stubs)
- **Admin bootstrap:** BROKEN (critical blocker)
- **Security hardening:** NOT DONE (localStorage, hardcoded creds, no MFA)
