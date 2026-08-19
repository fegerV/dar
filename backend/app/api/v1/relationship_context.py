from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.recipients import RecipientRepository
from app.schemas.relationship import (
    RecipientGroupCreate,
    RecipientGroupResponse,
    RelationshipSubtypeResponse,
    SharedMemoryCreate,
    SharedMemoryResponse,
)
from app.services.relationships.service import RelationshipContextService

router = APIRouter(prefix="/relationship-context", tags=["Relationship Context"])


@router.get("/subtypes", response_model=list[RelationshipSubtypeResponse])
async def list_subtypes(
    parent_code: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = RelationshipContextService(db)
    items = await service.list_subtypes(parent_code)
    return [RelationshipSubtypeResponse.model_validate(i) for i in items]


@router.post("/groups", response_model=RecipientGroupResponse, status_code=201)
async def create_group(
    body: RecipientGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RelationshipContextService(db)
    group = await service.create_group(current_user.id, body.code, body.title)
    await db.commit()
    return RecipientGroupResponse.model_validate(group)


@router.get("/groups", response_model=list[RecipientGroupResponse])
async def list_groups(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RelationshipContextService(db)
    groups = await service.list_groups(current_user.id)
    return [RecipientGroupResponse.model_validate(g) for g in groups]


@router.post("/shared-memories", response_model=SharedMemoryResponse, status_code=201)
async def create_shared_memory(
    body: SharedMemoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    recipient_repo = RecipientRepository(db)
    recipient = await recipient_repo.get_by_id(body.recipient_id, current_user.id)
    if recipient is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Recipient not found")

    service = RelationshipContextService(db)
    memory = await service.create_shared_memory(
        recipient_id=body.recipient_id,
        title=body.title,
        description=body.description,
        tags=body.tags,
        group_id=body.group_id,
        remind_before_days=body.remind_before_days,
    )
    await db.commit()
    return SharedMemoryResponse.model_validate(memory)


@router.get("/shared-memories/{recipient_id}", response_model=list[SharedMemoryResponse])
async def list_shared_memories(
    recipient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    recipient_repo = RecipientRepository(db)
    recipient = await recipient_repo.get_by_id(recipient_id, current_user.id)
    if recipient is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Recipient not found")
    service = RelationshipContextService(db)
    memories = await service.list_shared_memories(recipient_id)
    return [SharedMemoryResponse.model_validate(m) for m in memories]
