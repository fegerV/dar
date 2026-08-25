import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException, ValidationException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.audit import AuditLog
from app.models.email_verification import EmailVerification
from app.models.payment import Entitlement, Wallet
from app.models.referral import ReferralCode
from app.models.user import User, UserAuthIdentity, UserPreferences
from app.repositories.entitlements import EntitlementRepository
from app.repositories.refresh_tokens import RefreshTokenRepository
from app.repositories.users import UserRepository
from app.services.analytics.service import AnalyticsService


class AuthService:
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register(
        self, email: str, password: str, display_name: str | None = None
    ) -> dict:
        self._validate_password(password)

        user = User(
            email=email,
            display_name=display_name,
            status="active",
        )

        try:
            await self.repo.create(user)

            identity = UserAuthIdentity(
                user_id=user.id,
                provider="email",
                provider_user_id=email,
                email=email,
                credentials_json={"password_hash": hash_password(password)},
            )
            await self.repo.create_auth_identity(identity)

            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            existing = await self.repo.get_by_email(email)
            if existing:
                raise ConflictException("User with this email already exists")
            raise ConflictException("A user with this email already exists")

        wallet = Wallet(
            user_id=user.id,
            balance_rub=0,
            bonus_balance=0,
        )
        self.db.add(wallet)

        prefs = UserPreferences(
            user_id=user.id,
            preferred_moods=[],
            preferred_styles=[],
            notification_settings={},
            marketing_opt_in=False,
            analytics_opt_in=True,
        )
        self.db.add(prefs)

        entitlement = Entitlement(
            user_id=user.id,
            code="welcome_generation",
            quantity=1,
            consumed=0,
            source="registration",
            created_at=datetime.now(UTC),
        )
        entitlement_repo = EntitlementRepository(self.db)
        await entitlement_repo.create(entitlement)

        referral_code = ReferralCode(
            user_id=user.id,
            code=self._generate_referral_code(),
            is_active=True,
            uses_count=0,
        )
        self.db.add(referral_code)

        now = datetime.now(UTC)
        verification_token = secrets.token_urlsafe(32)
        verification_token_hash = hash_password(verification_token)
        email_verif = EmailVerification(
            user_id=user.id,
            email=email,
            token_hash=verification_token_hash,
            verified=False,
            expires_at=now + timedelta(hours=24),
        )
        self.db.add(email_verif)

        audit = AuditLog(
            actor_user_id=user.id,
            action="user.registered",
            target_type="user",
            target_id=user.id,
            metadata_={"email": email, "method": "email_password"},
            created_at=now,
        )
        self.db.add(audit)

        user_id = user.id

        await self.db.flush()
        from app.models.webhook import WebhookEndpoint

        webhook_payload = {
            "user_id": str(user.id),
            "email": email,
            "display_name": display_name,
            "registered_at": now.isoformat(),
        }
        try:
            result = await self.db.execute(
                select(WebhookEndpoint).where(WebhookEndpoint.is_active.is_(True))
            )
            active_webhooks = list(result.scalars().all())
        except Exception:
            active_webhooks = []

        await self.db.commit()

        analytics = AnalyticsService(self.db)
        try:
            await analytics.track_event(
                event_name="register",
                user_id=user_id,
                properties={"method": "email_password", "display_name_set": display_name is not None},
            )
            await self.db.commit()
        except Exception:
            pass

        await self._send_email_verification(email, verification_token)

        for endpoint in active_webhooks:
            if "user.registered" not in endpoint.events:
                continue
            try:
                import httpx
                import json as _json
                import hashlib
                import hmac as _hmac

                body = _json.dumps(
                    {"event": "user.registered", "data": webhook_payload},
                    default=str,
                )
                headers = {"Content-Type": "application/json", "User-Agent": "Daragent-Webhook/1.0"}
                if endpoint.secret:
                    sig = _hmac.new(
                        endpoint.secret.encode("utf-8"),
                        body.encode("utf-8"),
                        hashlib.sha256,
                    ).hexdigest()
                    headers["X-Daragent-Signature"] = f"sha256={sig}"

                async with httpx.AsyncClient(timeout=10) as client:
                    await client.post(endpoint.url, headers=headers, content=body)
            except Exception:
                pass

        return await self._make_tokens(user_id)

    async def login(self, email: str, password: str) -> dict:
        user = await self.repo.get_by_email(email)
        if not user or user.status != "active":
            raise UnauthorizedException("Invalid credentials")

        identity = await self.repo.get_auth_identity("email", email)
        if not identity:
            raise UnauthorizedException("Invalid credentials")

        stored_hash = identity.credentials_json.get("password_hash", "")
        if not verify_password(password, stored_hash):
            raise UnauthorizedException("Invalid credentials")

        return await self._make_tokens(user.id)

    async def oauth_login(self, provider: str, access_token: str, id_token: str | None = None) -> dict:
        from app.services.auth.oauth_service import OAuthService

        oauth_service = OAuthService(self.db)
        try:
            provider_info = await oauth_service._fetch_provider_info(provider, access_token)
        except Exception:
            raise UnauthorizedException("Invalid provider token")

        provider_user_id = f"{provider}:{provider_info['id']}"

        identity = await self.repo.get_auth_identity(provider, provider_user_id)

        if identity:
            identity.last_login_at = datetime.now(UTC)
            user = await self.repo.get_by_id(identity.user_id)
            if not user or user.status != "active":
                raise UnauthorizedException("User not found or inactive")
            return await self._make_tokens(user.id)

        email = provider_info.get("email")
        existing_user = await self.repo.get_by_email(email) if email else None

        if existing_user:
            await oauth_service.link_provider(existing_user.id, provider, access_token)
            return await self._make_tokens(existing_user.id)

        user = User(
            email=email,
            display_name=provider_info.get("name"),
            status="active",
        )
        await self.repo.create(user)

        identity = UserAuthIdentity(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            credentials_json={"access_token": access_token},
        )
        await self.repo.create_auth_identity(identity)

        wallet = Wallet(user_id=user.id, balance_rub=0, bonus_balance=0)
        self.db.add(wallet)

        prefs = UserPreferences(
            user_id=user.id,
            preferred_moods=[],
            preferred_styles=[],
            notification_settings={},
            marketing_opt_in=False,
            analytics_opt_in=True,
        )
        self.db.add(prefs)

        referral_code = ReferralCode(
            user_id=user.id,
            code=self._generate_referral_code(),
            is_active=True,
            uses_count=0,
        )
        self.db.add(referral_code)

        await self.db.commit()

        analytics = AnalyticsService(self.db)
        try:
            await analytics.track_event(
                event_name="register",
                user_id=user.id,
                properties={"method": f"oauth_{provider}"},
            )
        except Exception:
            pass

        return await self._make_tokens(user.id)

    async def refresh(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedException("Invalid refresh token")

        if await self.token_repo.is_revoked(jti):
            raise UnauthorizedException("Refresh token revoked")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")

        user = await self.repo.get_by_id(UUID(user_id))
        if not user or user.status != "active":
            raise UnauthorizedException("User not found or inactive")

        await self.token_repo.revoke_by_jti(jti)

        return await self._make_tokens(user.id)

    async def logout(self, refresh_token: str) -> None:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        jti = payload.get("jti")
        if jti:
            await self.token_repo.revoke_by_jti(jti)
        await self.db.commit()

    async def logout_all(self, user_id: UUID) -> None:
        await self.token_repo.revoke_all_for_user(user_id)
        await self.db.commit()

    def _validate_password(self, password: str) -> None:
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise ValidationException(
                f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters"
            )
        if len(password) > self.MAX_PASSWORD_LENGTH:
            raise ValidationException(
                f"Password must be at most {self.MAX_PASSWORD_LENGTH} characters"
            )
        if not any(c.isupper() for c in password):
            raise ValidationException(
                "Password must contain at least one uppercase letter"
            )
        if not any(c.islower() for c in password):
            raise ValidationException(
                "Password must contain at least one lowercase letter"
            )
        if not any(c.isdigit() for c in password):
            raise ValidationException("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            raise ValidationException(
                "Password must contain at least one special character"
            )

    def _generate_referral_code(self) -> str:
        return f"R{secrets.token_hex(4).upper()}"

    async def _send_email_verification(self, email: str, token: str) -> None:
        pass

    async def _make_tokens(self, user_id: UUID) -> dict:
        access_jti = secrets.token_urlsafe(32)
        refresh_jti = secrets.token_urlsafe(32)

        await self.token_repo.create(user_id, refresh_jti)

        return {
            "access_token": create_access_token(user_id, jti=access_jti),
            "refresh_token": create_refresh_token(user_id, jti=refresh_jti),
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
