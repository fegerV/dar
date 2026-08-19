"""Integration tests for the generation flow.

Tests the full path: create project → start generation → verify
generation record and job exist in database.
"""
from uuid import uuid4

import pytest

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.generation import Generation, GenerationJob, GenerationStep
from app.models.payment import Entitlement, Payment
from app.models.project import Project
from app.schemas.generation import GenerationStartRequest


def _grant_welcome_entitlement(db_session, user_id):
    entitlement = Entitlement(
        user_id=user_id,
        code="welcome_generation",
        quantity=1,
        consumed=0,
        source="test",
    )
    db_session.add(entitlement)
    return entitlement


@pytest.mark.asyncio
async def test_start_generation_creates_records(db_session, test_user):
    from app.services.generations.service import GenerationService

    project = Project(owner_user_id=test_user.id, title="Test Project", status="brief_completed")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    _grant_welcome_entitlement(db_session, test_user.id)
    await db_session.commit()

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

    entitlement_result = await db_session.execute(
        select(Entitlement).where(Entitlement.user_id == test_user.id)
    )
    entitlement = entitlement_result.scalar_one()
    assert entitlement.consumed == 1


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

    _grant_welcome_entitlement(db_session, test_user.id)
    await db_session.commit()

    service = GenerationService(db_session)
    first_body = GenerationStartRequest(force_regenerate=True, variables={})
    await service.start_generation(project.id, test_user.id, first_body)

    second_body = GenerationStartRequest(force_regenerate=False, variables={})
    with pytest.raises(ConflictException):
        await service.start_generation(project.id, test_user.id, second_body)


@pytest.mark.asyncio
async def test_generation_without_payment_or_entitlement_rejected(db_session, test_user):
    """VULN-01: Generation should require payment or entitlement."""
    from app.services.generations.service import GenerationService

    project = Project(
        owner_user_id=test_user.id,
        title="Paid Project",
        status="brief_completed",
        price_rub=590.0,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    service = GenerationService(db_session)
    body = GenerationStartRequest(force_regenerate=False, variables={})
    with pytest.raises(ValidationException, match="Payment required"):
        await service.start_generation(project.id, test_user.id, body)


@pytest.mark.asyncio
async def test_generation_with_paid_project_allowed(db_session, test_user):
    """Paid project (paid_rub > 0) should allow generation without entitlement."""
    from app.services.generations.service import GenerationService

    project = Project(
        owner_user_id=test_user.id,
        title="Paid Project",
        status="brief_completed",
        price_rub=590.0,
        paid_rub=590.0,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    service = GenerationService(db_session)
    body = GenerationStartRequest(force_regenerate=True, variables={})
    response = await service.start_generation(project.id, test_user.id, body)
    assert response is not None
    assert response.status == "queued"


@pytest.mark.asyncio
async def test_generation_with_paid_payment_record_allowed(db_session, test_user):
    """Generation allowed if a 'paid' Payment record exists for the project."""
    from app.services.generations.service import GenerationService

    project = Project(
        owner_user_id=test_user.id,
        title="Paid Project",
        status="brief_completed",
        price_rub=590.0,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    payment = Payment(
        user_id=test_user.id,
        project_id=project.id,
        provider_id=uuid4(),
        status="paid",
        method="bank_card",
        amount_rub=590.0,
        bonus_amount_rub=0,
        discount_rub=0,
        provider_payload={},
    )
    db_session.add(payment)
    await db_session.commit()

    service = GenerationService(db_session)
    body = GenerationStartRequest(force_regenerate=True, variables={})
    response = await service.start_generation(project.id, test_user.id, body)
    assert response.status == "queued"


@pytest.mark.asyncio
async def test_entitlement_consumed_once(db_session, test_user):
    """VULN-02: Welcome entitlement should be consumed and not reusable."""
    from app.services.generations.service import GenerationService

    project = Project(
        owner_user_id=test_user.id,
        title="Free Project",
        status="brief_completed",
        price_rub=0.0,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    _grant_welcome_entitlement(db_session, test_user.id)
    await db_session.commit()

    service = GenerationService(db_session)

    body = GenerationStartRequest(force_regenerate=True, variables={})
    response = await service.start_generation(project.id, test_user.id, body)
    assert response.status == "queued"

    # Second generation should fail — entitlement consumed
    body2 = GenerationStartRequest(force_regenerate=True, variables={})
    with pytest.raises(ValidationException, match="Entitlement required"):
        await service.start_generation(project.id, test_user.id, body2)


@pytest.mark.asyncio
async def test_force_regenerate_cancels_existing(db_session, test_user):
    """VULN-06: force_regenerate should cancel existing active generation."""
    from app.services.generations.service import GenerationService

    project = Project(
        owner_user_id=test_user.id,
        title="Test Project",
        status="brief_completed",
        price_rub=0.0,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    _grant_welcome_entitlement(db_session, test_user.id)
    await db_session.commit()

    service = GenerationService(db_session)
    first_body = GenerationStartRequest(force_regenerate=True, variables={})
    first_response = await service.start_generation(project.id, test_user.id, first_body)

    _grant_welcome_entitlement(db_session, test_user.id)
    await db_session.commit()

    second_body = GenerationStartRequest(force_regenerate=True, variables={})
    second_response = await service.start_generation(project.id, test_user.id, second_body)

    assert second_response.id != first_response.id
    first_gen = await db_session.get(Generation, first_response.id)
    assert first_gen.status == "cancelled"
