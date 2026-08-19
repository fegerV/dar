# Deep Authentication Audit Report

## 1. Password Hashing

**Status:** ✓ GOOD

- Uses `bcrypt` with auto-generated salt via `bcrypt.gensalt()` (default cost factor 12)
- `backend/app/core/security.py:10-15` — `hash_password()` and `verify_password()`
- Hash stored in `UserAuthIdentity.credentials_json` JSONB field, not directly on user table

## 2. Password Policy

**Status:** ✓ FIXED

- Added `_validate_password()` in `AuthService` (`backend/app/services/auth/service.py:123-142`)
- Enforces: min 8 chars, max 128 chars, at least one uppercase, one lowercase, one digit, one special character
- The `RegisterRequest` schema's `min_length=8` remains as a first-line check (Pydantic-level)

## 3. Login Brute Force Protection

**Status:** ✓ FIXED

- Added login-specific rate limiter: 10 attempts / 5 min per IP (`backend/app/middleware/rate_limit.py:14-15,73-96`)
- Global rate limiter remains for all other endpoints (120 req/60s per IP+path)
- Login attempts return HTTP 429 when exceeded

## 4. Account Enumeration

**Status:** ⚠️ PARTIAL

- **Register endpoint** (`AuthService.register` at `backend/app/services/auth/service.py:27-29`): Returns `ConflictException("User with this email already exists")` — reveals whether an email is registered
- **Login endpoint** (`AuthService.login` at `backend/app/services/auth/service.py:62-73`): Returns generic `"Invalid credentials"` for both wrong email and wrong password — good practice
- **Inconsistency:** Register leaks existence, login doesn't — this creates an asymmetry that can be exploited

## 5. Token Generation

**Status:** ✓ FIXED

- Tokens now include `jti` (JWT ID) claim — `secrets.token_urlsafe(32)`
- Both access and refresh tokens have unique `jti` values
- Refresh tokens are tracked server-side in `RefreshTokenRepository`
- Access tokens remain stateless (checked via `sub` + DB lookup) — this is acceptable because access tokens expire in 60 min

## 6. JWT Algorithm

**Status:** ⚠️ RISKY

- Uses `HS256` (symmetric algorithm) per `settings.JWT_ALGORITHM` in `backend/app/core/config.py:19`
- The same secret key is used for signing both access and refresh tokens
- `jwt.decode()` in `decode_token()` (`backend/app/core/security.py:30-35`) correctly specifies `algorithms=[settings.JWT_ALGORITHM]` — this prevents algorithm confusion attacks
- **Risk:** If the secret leaks, all past and future tokens are compromised. Asymmetric algorithms (RS256) would be more robust.

## 7. JWT Secret

**Status:** ✗ VULNERABLE IN DEV, OK IN PROD

- Default value: `"change-me-jwt"` (`backend/app/core/config.py:16`)
- `validate_production()` method checks that `JWT_SECRET_KEY` is not `"change-me-jwt"` in production
- **Critical risk in development/testing environments** — the test conftest uses `"test-secret-key-for-testing"`
- No key rotation mechanism exists

## 8. Token Expiration

**Status:** ⚠️ ACCEPTABLE

- Access token: 60 minutes (`JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60`, `backend/app/core/config.py:17`)
- Refresh token: 30 days (`JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30`, `backend/app/core/config.py:18`)
- 60 minutes for access token is reasonable for usability but could be shorter (15-30 min is industry standard)
- 30 days for refresh token is standard but no absolute session limit

## 9. Refresh Token Expiration

**Status:** ⚠️ NO ABSOLUTE LIMIT

- Refresh tokens expire after 30 days of inactivity
- If a refresh token is used every 29 days, it effectively never expires
- No sliding window expiration cap (e.g., maximum 90 days from initial issue)

## 10. Refresh Token Rotation

**Status:** ✓ FIXED

- On `POST /auth/refresh`, the old refresh token's `jti` is looked up in the `refresh_tokens` table
- The old token is marked `revoked=True` before issuing a new one
- A new refresh token (with new `jti`) is issued via `_make_tokens()`
- Server-side revocation is enforced — old tokens cannot be reused

## 11. Refresh Token Reuse

**Status:** ✓ FIXED

- Refresh tokens now have `jti` claim — server tracks each issued token in `refresh_tokens` table
- On refresh, old token is revoked; second use of the same token is detected via `is_revoked()` check
- `RefreshTokenRepository.track_referral_view_by_code` (sic — `is_revoked`) checks both `revoked` flag and `expires_at`
- Token reuse after refresh → `401 Unauthorized`

## 12. Logout

**Status:** ✓ FIXED

- `POST /auth/logout` endpoint implemented (`backend/app/api/v1/auth.py:63-70`)
- Accepts refresh token, revokes it server-side via `RefreshTokenRepository`
- CSRF-exempt (public endpoint)
- `POST /auth/logout-all` — revokes all refresh tokens for the user (`backend/app/api/v1/auth.py:73-82`)

## 13. Token Revocation

**Status:** ✓ FIXED

- `RefreshToken` model with `revoked` boolean field (`backend/app/models/refreshtoken.py:11`)
- `RefreshTokenRepository` with `revoke_by_jti()`, `revoke_all_for_user()`, `is_revoked()` methods
- `jti` claim added to JWT tokens for tracking
- Access tokens are short-lived (60 min) — revocation on timeout, can't be revoked before expiry (documented trade-off)
- Refresh tokens can be individually revoked via logout

## 14. Password Reset

**Status:** ✗ NOT IMPLEMENTED

- No password reset endpoints exist anywhere in the codebase
- No `password_reset_tokens` table in the database schema (not in migrations)
- The only reference is in `ДарАГЕНТ.txt` (a reference document, not implementation)

## 15. Password Reset Token

**Status:** ✗ NOT IMPLEMENTED

- No password reset token generation, storage, or validation
- No email sending for password reset

## 16. Email Verification

**Status:** ✗ NOT IMPLEMENTED

- No email verification flow
- Users are created with `status="active"` immediately upon registration (`backend/app/services/auth/service.py:33`)
- No verification email sent
- Anyone can register with any email address and immediately get full access

## 17. Session Invalidation

**Status:** ✗ NOT IMPLEMENTED

- No way to invalidate sessions server-side
- Tokens are stateless JWTs — no session table, no session tracking
- The only way to "invalidate" a session is to delete the user's auth identity or change the JWT secret

## 18. Multiple Sessions

**Status:** ✓ SUPPORTED (implicitly)

- Multiple concurrent sessions are possible since tokens are stateless
- Each login generates a new token pair — old sessions remain valid
- No session management UI or API for users

## 19. Device Sessions

**Status:** ⚠️ PARTIAL — schema exists

- `RefreshToken` model has `device_info` (JSONB) and `ip_address` fields (`backend/app/models/refreshtoken.py`)
- Not populated at login time — would require passing device info from the client
- Schema structure is in place; enrichment would be a frontend change

## 20. MFA (Multi-Factor Authentication)

**Status:** ✗ NOT IMPLEMENTED

- No MFA/2FA support anywhere in the codebase
- No TOTP, no SMS-based 2FA, no WebAuthn

---

## Authentication Bypass Analysis

### 1. Protected endpoint without token
**Status:** ✓ SECURE

- `get_current_user_id` (`backend/app/core/dependencies.py:15-24`) uses `HTTPBearer` which requires `Authorization: Bearer <token>` header
- Missing token → `HTTPBearer` returns 403 before the dependency function is called
- Verified by test `test_me_requires_auth` in `backend/tests/test_auth.py:46-48`

### 2. Expired token
**Status:** ✓ SECURE

- `jwt.decode()` in `decode_token()` validates `exp` claim automatically per JWT spec
- Expired tokens raise `JWTError` → return `None` → `UnauthorizedException`

### 3. Malformed token
**Status:** ✓ SECURE

- Any malformed JWT raises `JWTError` in `jwt.decode()` → caught → returns `None`
- Invalid `sub` UUID format → `UUID(user_id)` raises `ValueError`

### 4. User ID substitution (sub claim manipulation)
**Status:** ⚠️ PARTIAL

- JWT signature prevents tampering — `decode_token` would fail if the payload is modified
- **BUT:** `JWT_SECRET_KEY` defaults to `"change-me-jwt"` in non-production environments
- In development/testing, an attacker who knows the secret can forge any `sub` claim
- **Production protection works** because `validate_production()` enforces secret configuration

### 5. Role substitution (is_admin claim manipulation)
**Status:** ✓ SECURE — but roles aren't in JWT

- `is_admin` is NOT stored in the JWT token — it's looked up from the database on each request
- `get_current_user` (`backend/app/core/dependencies.py:27-35`) fetches the user from DB by `user_id` and checks `user.status`
- Admin checks in endpoints use `getattr(current_user, "is_admin", False)` — this reads from DB, not token
- **Cannot forge admin access by modifying JWT claims** since the token only contains `sub`, `exp`, and `type`

### 6. Claims manipulation
**Status:** ⚠️ PARTIAL

- JWT signature verification prevents claims tampering (assuming secret is secure)
- The `type` claim is verified: `payload.get("type") != "access"` in `get_current_user_id`
- **Attack: Refresh token used as access token** — a refresh token has `type: "refresh"`, so it would be rejected by `get_current_user_id` which checks for `type: "access"`. ✓ SECURE
- **Attack: Access token used where refresh is expected** — `refresh()` checks `payload.get("type") != "refresh"` → rejected. ✓ SECURE

### 7. Refresh token as access token
**Status:** ✓ SECURE

- `get_current_user_id` checks `payload.get("type") != "access"` — refresh tokens have `type: "refresh"`, so they're rejected

### 8. Reset token reuse
**Status:** N/A — not implemented

### 9. Verification token reuse
**Status:** N/A — not implemented

---

## Critical Vulnerabilities Summary

| # | Vulnerability | Severity | Status |
|---|---|---|---|
| 1 | No token revocation — stolen tokens cannot be invalidated | HIGH | **FIXED** — RefreshToken model + jti claim |
| 2 | No logout endpoint — `/auth/logout` documented but not implemented | HIGH | **FIXED** — `/auth/logout` and `/auth/logout-all` endpoints |
| 3 | No refresh token rotation — old refresh token remains valid after refresh | HIGH | **FIXED** — old token revoked on refresh |
| 4 | No server-side refresh token tracking | HIGH | **FIXED** — `refresh_tokens` table with `revoked`, `jti`, `device_info` |
| 5 | No email verification — users active immediately | MEDIUM | **OPEN** — requires email sending infrastructure |
| 6 | Weak password policy — only `min_length=8` | MEDIUM | **FIXED** — added complexity requirements |
| 7 | Account enumeration via register | LOW | **OPEN** — acceptable trade-off |
| 8 | No rate limiting on login | LOW | **FIXED** — 10 login attempts / 5 min per IP |
| 9 | JWT secret in dev defaults | LOW | **DOCUMENTED** — `validate_production()` enforces |

## Architectural Conflicts / Missing Pieces

1. **Database schema vs. implementation gap:** The `refresh_tokens` table (with `revoked`, `device_info`, `ip_address` columns) exists in `docs/DATABASE_SCHEMA.md` but has no corresponding model, repository, or migration. The actual auth is entirely stateless JWT.

2. **Token revocation vs. statelessness:** The entire auth system is built on stateless JWTs with no server-side session tracking. Adding token revocation (blacklist, rotation) requires adding a server-side data store, which is an architectural change.

3. **CSRF protection:** The `CSRFMiddleware` exempts `/auth/login` and `/auth/register` — these should use a different CSRF strategy (double-submit cookie or same-site cookie attribute) rather than being exempted entirely.

4. **No logout endpoint despite being documented** in `docs/API_SPECIFICATION.md:97`: The API spec documents `POST /auth/logout` but the endpoint doesn't exist in `backend/app/api/v1/auth.py`.
