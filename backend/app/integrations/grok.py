"""Grok AI integration for script generation and personalization."""
import httpx

from app.core.config import settings


class GrokClient:
    BASE_URL = "https://api.x.ai/v1"

    def __init__(self):
        self.api_key = settings.GROK_API_KEY
        self.model = settings.GROK_MODEL

    async def generate_script(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> dict:
        if not self.api_key:
            return {"error": "GROK_API_KEY not configured", "script": None}

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "script": content,
                "usage": data.get("usage", {}),
                "model": data.get("model", self.model),
            }

    async def personalize_brief(self, brief_data: dict, recipient_data: dict) -> dict:
        system_prompt = (
            "Ты — эксперт по персонализации видеопоздравлений. "
            "На основе брифа и данных о получателе предложи улучшения."
        )
        user_prompt = f"Бриф: {brief_data}\nПолучатель: {recipient_data}"
        return await self.generate_script(system_prompt, user_prompt)
