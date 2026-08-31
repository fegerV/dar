import uuid
from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserAuthIdentity


class OAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def link_provider(
        self,
        user_id: uuid.UUID,
        provider: str,
        access_token: str,
    ) -> UserAuthIdentity:
        provider_user_info = await self._fetch_provider_info(provider, access_token)
        provider_user_id = f"{provider}:{provider_user_info['id']}"

        existing = await self.db.execute(
            select(UserAuthIdentity).where(
                UserAuthIdentity.provider == provider,
                UserAuthIdentity.provider_user_id == provider_user_id,
            )
        )
        identity = existing.scalar_one_or_none()
        if identity and identity.user_id != user_id:
            raise ValueError("Provider already linked to another account")
        if identity:
            identity.last_login_at = datetime.now(UTC)
            await self.db.flush()
            return identity

        identity = UserAuthIdentity(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=provider_user_info.get("email"),
            credentials_json={"access_token": access_token},
        )
        self.db.add(identity)
        await self.db.flush()
        return identity

    async def _fetch_provider_info(
        self, provider: str, access_token: str
    ) -> dict:
        if provider == "yandex":
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://login.yandex.ru/info",
                    headers={"Authorization": f"OAuth {access_token}"},
                    params={"format": "json"},
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "id": data.get("id") or data.get("client_id"),
                    "email": data.get("default_email"),
                    "name": data.get("real_name") or data.get("display_name"),
                }
        elif provider == "vk":
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.vk.com/method/users.get",
                    params={
                        "access_token": access_token,
                        "v": "5.131",
                        "fields": "photo_200,bdate,email",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                user = data["response"][0]
                return {
                    "id": str(user["id"]),
                    "email": data.get("email"),
                    "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                }
        raise ValueError(f"Unsupported provider: {provider}")
