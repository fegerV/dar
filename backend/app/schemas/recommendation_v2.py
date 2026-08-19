from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    project_id: UUID
    top_k: int = 5
    use_ai_rerank: bool = True
    use_diversity: bool = True


class RecommendationItem(BaseModel):
    rank: int
    template_version_id: UUID
    score: float
    match_reasons: list[str] = []
    explanation: str | None = None
    concept_title: str | None = None


class RecommendationListResponseV2(BaseModel):
    items: list[RecommendationItem]
    generated_at: datetime
    model_version: str = "rule_based_v2"
