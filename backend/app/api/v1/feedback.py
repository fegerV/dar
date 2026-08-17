from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.feedback import Feedback
from app.repositories.feedback import FeedbackRepository

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    generation_id: UUID
    reaction: str
    details: str | None = None


class FeedbackResponse(BaseModel):
    id: UUID
    generation_id: UUID
    reaction: str
    details: str | None = None

    model_config = {"from_attributes": True}


@router.post("", response_model=FeedbackResponse)
async def create_feedback(
    body: FeedbackRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = FeedbackRepository(db)
    feedback = Feedback(
        user_id=current_user.id,
        generation_id=body.generation_id,
        reaction=body.reaction,
        details=body.details,
    )
    feedback = repo.db.add(feedback)
    await db.commit()
    return FeedbackResponse.model_validate(feedback)
