import hashlib
from uuid import UUID

from app.core.config import settings
from app.integrations.ai.base import BaseTextProvider


class GrokTextProvider(BaseTextProvider):
    provider_id: UUID = UUID(int=0)

    def __init__(self):
        self.name = "grok"
        self.api_key = settings.GROK_API_KEY
        self.model = settings.GROK_MODEL
        self.enabled = bool(self.api_key)

    async def healthcheck(self) -> bool:
        return self.enabled

    def estimate_cost(self, task: dict[str, Any]) -> float:
        return 0.0

    async def generate_text(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"text": None, "error": "Grok provider disabled"}

        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": parameters.get("system_prompt", "")},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": parameters.get("temperature", 0.7),
                    "max_tokens": parameters.get("max_tokens", 2000),
                },
            )
            data = response.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"text": text, "usage": data.get("usage", {}), "model": data.get("model", self.model)}
