"""Integration tests for the generation flow.

Tests the full path: create project → start generation → verify
generation record and job exist in database.
"""
import pytest
from uuid import uuid4

from app.core.exceptions import ConflictException, NotFoundException
from app.models.project import Project
from app.models.generation import Generation, GenerationJob, GenerationStep
from app.schemas.generation import GenerationStartRequest


@pytest.mark.asyncio
async def test_start_generation_creates_records(db_session, test_user):
    from app.services.generations.service import GenerationService

    project = Project(owner_user_id=test_user.id, title="Test Project", status="brief_completed")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    service = GenerationService(db_session)
    body = GenerationStartRequest(force_regenerate=True, variables={"prompt": "test prompt"})
    response = await service.start_generation(project.id, test_user.id, body)

    assert response is not None
    assert response.status == "queued"

    from sqlalchemy import select
    gen_result = await db_session.execute(
        select(Generation).where(Generation.project_id == project.id)
    )
    generation = gen_result.scalar_one_or_none()
    assert generation is not None
    assert generation.status == "queued"
    assert generation.type == "final"

    steps_result = await db_session.execute(
        select(GenerationStep).where(GenerationStep.generation_id == generation.id)
    )
    steps = steps_result.scalars().all()
    assert len(steps) == 3
    step_codes = [s.step_code for s in steps]
    assert "script" in step_codes
    assert "voice" in step_codes
    assert "video" in step_codes

    job_result = await db_session.execute(
        select(GenerationJob).where(GenerationJob.generation_id == generation.id)
    )
    job = job_result.scalar_one_or_none()
    assert job is not None
    assert job.status == "queued"
    assert job.queue_name == "generation"


@pytest.mark.asyncio
async def test_start_generation_not_found(db_session, test_user):
    from app.services.generations.service import GenerationService

    service = GenerationService(db_session)
    body = GenerationStartRequest(force_regenerate=False, variables={})
    with pytest.raises(NotFoundException):
        await service.start_generation(uuid4(), test_user.id, body)


@pytest.mark.asyncio
async def test_start_generation_forbidden(db_session, test_user):
    from app.services.generations.service import GenerationService

    other_user_id = uuid4()
    project = Project(owner_user_id=other_user_id, title="Other's Project", status="brief_completed")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    service = GenerationService(db_session)
    body = GenerationStartRequest(force_regenerate=False, variables={})
    with pytest.raises(NotFoundException):
        await service.start_generation(project.id, test_user.id, body)


@pytest.mark.asyncio
async def test_start_generation_conflict_on_active(db_session, test_user):
    from app.services.generations.service import GenerationService

    project = Project(owner_user_id=test_user.id, title="Test Project", status="brief_completed")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    service = GenerationService(db_session)
    first_body = GenerationStartRequest(force_regenerate=True, variables={})
    await service.start_generation(project.id, test_user.id, first_body)

    second_body = GenerationStartRequest(force_regenerate=False, variables={})
    with pytest.raises(ConflictException):
        await service.start_generation(project.id, test_user.id, second_body)
