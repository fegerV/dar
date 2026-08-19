import json
import logging
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.schemas.template_render import RenderTemplateResponse

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 86400
CACHE_TABLE = "template_render_cache"


class TemplateCacheManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def init_schema(self) -> None:
        try:
            await self.db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {CACHE_TABLE} (
                    template_version_id UUID PRIMARY KEY,
                    rendered_json JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """))
            await self.db.execute(text(
                f"CREATE INDEX IF NOT EXISTS ix_{CACHE_TABLE}_expires ON {CACHE_TABLE} (expires_at)"
            ))
            await self.db.commit()
        except Exception as e:
            logger.error("Failed to initialize render cache schema: %s", e)

    async def get_rendered_template(
        self, template_version_id: object
    ) -> "RenderTemplateResponse | None":
        try:
            result = await self.db.execute(text(f"""
                SELECT rendered_json FROM {CACHE_TABLE}
                WHERE template_version_id = :tid
                  AND expires_at > NOW()
            """), {"tid": str(template_version_id)})
            row = result.fetchone()
            if row is None:
                return None
            data = row[0]
            if isinstance(data, str):
                data = json.loads(data)

            return RenderTemplateResponse.model_validate(data)
        except Exception as e:
            logger.error("Cache get failed: %s", e)
            return None

    async def store_rendered_template(
        self, template_version_id: object, result: "RenderTemplateResponse"
    ) -> None:
        try:
            expires = datetime.now(UTC) + timedelta(seconds=CACHE_TTL_SECONDS)
            data = result.model_dump()
            await self.db.execute(text(f"""
                INSERT INTO {CACHE_TABLE}
                    (template_version_id, rendered_json, expires_at)
                VALUES
                    (:tid, :data::jsonb, :expires)
                ON CONFLICT (template_version_id) DO UPDATE
                    SET rendered_json = EXCLUDED.rendered_json,
                        expires_at = EXCLUDED.expires_at
            """), {
                "tid": str(template_version_id),
                "data": json.dumps(data),
                "expires": expires.isoformat(),
            })
            await self.db.commit()
        except Exception as e:
            logger.error("Cache store failed: %s", e)

    async def cleanup_expired(self) -> int:
        result = await self.db.execute(text(
            f"DELETE FROM {CACHE_TABLE} WHERE expires_at <= NOW()"
        ))
        await self.db.commit()
        return result.rowcount if result.rowcount is not None else 0

    async def get_cache_status(self) -> dict:
        try:
            result = await self.db.execute(text(
                f"SELECT COUNT(*) FROM {CACHE_TABLE}"
            ))
            count = result.scalar() or 0
            return {"cache_enabled": True, "cached_templates": count}
        except Exception:
            return {"cache_enabled": False, "cached_templates": 0}
