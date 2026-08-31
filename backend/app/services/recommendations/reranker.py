from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.recommendation import Recommendation
from app.repositories.projects import ProjectRepository
from app.repositories.recipients import RecipientRepository
from app.repositories.recommendations import RecommendationRepository, TemplateRepository
from app.schemas.recommendation_v2 import RecommendationItem, RecommendationListResponseV2


class AIReranker:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RecommendationRepository(db)
        self.template_repo = TemplateRepository(db)
        self.project_repo = ProjectRepository(db)
        self.recipient_repo = RecipientRepository(db)

    async def rerank(self, project_id: UUID, user_id: UUID, top_k: int = 5) -> RecommendationListResponseV2:
        candidates = await self.repo.list_by_project(project_id)
        if not candidates:
            return RecommendationListResponseV2(items=[], generated_at=datetime.now(UTC))

        project = await self.project_repo.get_by_id(project_id, user_id)
        if project is None:
            return RecommendationListResponseV2(items=[], generated_at=datetime.now(UTC))

        brief = await self.project_repo.get_brief(project_id)
        recipient = None
        if project.recipient_id:
            recipient = await self.recipient_repo.get_by_id(project.recipient_id, project.owner_user_id)

        payload = {
            "project": {
                "occasion_code": project.occasion_code,
                "occasion_title": project.occasion_title,
            },
            "recipient": {
                "name": recipient.first_name if recipient else None,
                "relationship": brief.relationship_ if brief else None,
                "interests": recipient.interests if recipient else [],
                "traits": recipient.traits if recipient else [],
            },
            "brief": {
                "desired_mood": brief.desired_mood if brief else None,
                "humor_level": brief.humor_level,
                "emotion_level": brief.emotion_level,
                "surprise_level": brief.surprise_level,
                "inside_joke": brief.inside_joke,
                "hobbies_text": brief.hobbies_text,
                "sender_message": brief.sender_message,
            },
            "candidates": [
                {
                    "id": str(c.template_version_id),
                    "rank": c.rank,
                    "score": float(c.score) if c.score else 0.0,
                    "match_reasons": c.match_reasons or [],
                }
                for c in candidates[:10]
            ],
        }

        prompt = (
            "Ты — эксперт по подбору концепций поздравлений.\n"
            "На входе кандидаты с их score и match_reasons.\n"
            "Переранжируй их с учётом смысла, не просто по score.\n"
            "Ответ строго в JSON:\n"
            '{"ranked": [{"template_version_id": "...", "score": 0.0, "reason": "..."}]}\n'
            f"Входные данные: {json.dumps(payload, ensure_ascii=False)}"
        )

        ranked = await self._call_grok(prompt)
        if not ranked:
            return self._to_response(candidates[:top_k])

        merged = []
        seen = set()
        for item in candidates:
            match = next((r for r in ranked if r.get("template_version_id") == str(item.template_version_id)), None)
            if match:
                score = float(match.get("score", item.score or 0.0))
                explanation = match.get("reason", item.explanation)
            else:
                score = item.score or 0.0
                explanation = item.explanation
            if item.template_version_id not in seen:
                merged.append((item, score, explanation))
                seen.add(item.template_version_id)

        merged.sort(key=lambda x: x[1], reverse=True)
        top = merged[:top_k]

        items = []
        for idx, (candidate, score, explanation) in enumerate(top, start=1):
            version = await self.template_repo.get_version_by_id(candidate.template_version_id)
            template = await self.template_repo.get_by_id(version.template_id) if version else None
            items.append(
                RecommendationItem(
                    rank=idx,
                    template_version_id=candidate.template_version_id,
                    score=score,
                    match_reasons=candidate.match_reasons or [],
                    explanation=explanation,
                    concept_title=template.title if template else None,
                )
            )

        return RecommendationListResponseV2(
            items=items,
            generated_at=datetime.now(UTC),
            model_version="ai_rerank_v1",
        )

    async def _call_grok(self, prompt: str) -> list[dict]:
        api_key = settings.GROK_API_KEY
        if not api_key:
            return []

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.GROK_MODEL,
                    "messages": [
                        {"role": "system", "content": "Ты — полезный ассистент. Отвечай только валидным JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000,
                },
            )
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            try:
                parsed = json.loads(content)
                return parsed.get("ranked", [])
            except Exception:
                return []

    def _to_response(self, candidates: list[Recommendation], top_k: int = 5) -> RecommendationListResponseV2:
        items = []
        for idx, c in enumerate(candidates[:top_k], start=1):
            items.append(
                RecommendationItem(
                    rank=idx,
                    template_version_id=c.template_version_id,
                    score=float(c.score or 0.0),
                    match_reasons=c.match_reasons or [],
                    explanation=c.explanation,
                )
            )
        return RecommendationListResponseV2(items=items, generated_at=datetime.now(UTC))


class DiversityFilter:
    def apply(self, items: list[RecommendationItem], limit: int = 5) -> list[RecommendationItem]:
        if len(items) <= limit:
            return items

        selected: list[RecommendationItem] = []
        candidates = list(items)

        while candidates and len(selected) < limit:
            best = None
            best_score = -999.0
            for idx, item in enumerate(candidates):
                relevance = item.score
                similarity = self._max_similarity(item, selected) if selected else 0.0
                mmr_score = relevance - 0.7 * similarity
                if mmr_score > best_score:
                    best_score = mmr_score
                    best = (idx, item)

            if best is None:
                break
            idx, item = best
            selected.append(item)
            candidates.pop(idx)

        for idx, item in enumerate(selected, start=1):
            item.rank = idx

        return selected

    def _max_similarity(self, candidate: RecommendationItem, selected: list[RecommendationItem]) -> float:
        max_sim = 0.0
        for item in selected:
            sim = self._similarity(candidate, item)
            max_sim = max(max_sim, sim)
        return max_sim

    def _similarity(self, a: RecommendationItem, b: RecommendationItem) -> float:
        reasons_a = set(a.match_reasons or [])
        reasons_b = set(b.match_reasons or [])
        if not reasons_a or not reasons_b:
            return 0.0
        return len(reasons_a & reasons_b) / len(reasons_a | reasons_b)
