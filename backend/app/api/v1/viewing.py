from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.viewing import ReactionRequest, ReactionResponse, ReactionStatsResponse
from app.services.viewing.reaction import ReactionService

router = APIRouter(prefix="/viewing", tags=["Viewing Feedback"])


@router.post("/projects/{project_id}/reaction", response_model=ReactionResponse, status_code=201)
async def add_reaction(
    project_id: UUID,
    body: ReactionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReactionService(db)
    reaction = await service.add_reaction(
        project_id=project_id,
        user_id=current_user.id,
        emoji=body.emoji.value,
        rating=body.rating,
        comment=body.comment,
        negative_details=body.negative_details,
    )
    await db.commit()
    return ReactionResponse.model_validate(reaction)


@router.get("/projects/{project_id}/reactions/stats", response_model=ReactionStatsResponse)
async def get_reaction_stats(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReactionService(db)
    return await service.get_stats(project_id, current_user.id)


@router.get("/projects/{project_id}/reactions/comments", response_model=list[dict])
async def get_comment_details(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReactionService(db)
    return await service.get_comment_details(project_id)
