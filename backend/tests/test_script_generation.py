"""Integration tests for Script Generation with AI fallback to cached templates."""
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.core.security import create_access_token
from app.models.brief import CreativeBrief
from app.models.generation import Generation, GenerationStep
from app.models.project import Project
from app.models.recipient import Recipient
from app.models.template import PromptTemplate
from app.services.script_generation.service import ScriptGenerationService


async def _create_project_with_brief(db_session, user_id):
    recipient = Recipient(
        owner_user_id=user_id,
        first_name="Alice",
        last_name="Smith",
    )
    db_session.add(recipient)
    await db_session.flush()

    project = Project(
        owner_user_id=user_id,
        recipient_id=recipient.id,
        title="Birthday Project",
        status="brief_completed",
        occasion_code="birthday",
        occasion_title="День рождения",
    )
    db_session.add(project)
    await db_session.flush()

    brief = CreativeBrief(
        project_id=project.id,
        status="completed",
        relationship_="friend",
        relationship_text="Close friend",
        desired_mood="funny",
        sender_message="Happy birthday!",
    )
    db_session.add(brief)
    await db_session.flush()
    return project, recipient, brief


@pytest.mark.asyncio
async def test_script_generation_fallback_to_cached_template(db_session, test_user):
    project, recipient, brief = await _create_project_with_brief(db_session, test_user.id)

    template = PromptTemplate(
        code="birthday_friend_template",
        name="Birthday Friend Template",
        category="birthday",
        text="Сценарий для {occasion}: {base_prompt} {relationship}",
        variables=["occasion", "relationship", "base_prompt"],
        is_active=True,
        success_rate=0.85,
    )
    db_session.add(template)

    gen = Generation(
        project_id=project.id,
        type="final",
        status="processing",
        requested_by_user_id=test_user.id,
        input_json={"brief": {}},
    )
    db_session.add(gen)
    await db_session.flush()

    step = GenerationStep(
        generation_id=gen.id,
        step_no=1,
        step_code="script",
        type="text",
        status="processing",
        input_json={"brief": {}},
    )
    db_session.add(step)
    await db_session.commit()

    service = ScriptGenerationService(db_session)
    result = await service.generate_script(
        project_id=project.id,
        owner_user_id=test_user.id,
        generation_step_id=step.id,
    )

    assert result["source"] == "fallback_template"
    assert "script" in result
    assert "occasion" not in result["script"]
    assert result["provider"] == "cached_template"

    step_result = await db_session.execute(
        select(GenerationStep).where(GenerationStep.id == step.id)
    )
    saved_step = step_result.scalar_one()
    assert saved_step.status == "completed"
    assert saved_step.output_json["source"] == "fallback_template"


@pytest.mark.asyncio
async def test_script_generation_fallback_no_template_uses_raw_prompt(db_session, test_user):
    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="Charlie",
        last_name="Brown",
    )
    db_session.add(recipient)
    await db_session.flush()

    project = Project(
        owner_user_id=test_user.id,
        recipient_id=recipient.id,
        title="New Year Project",
        status="brief_completed",
        occasion_code="new_year",
    )
    db_session.add(project)
    await db_session.flush()

    from app.models.brief import CreativeBrief
    brief = CreativeBrief(
        project_id=project.id,
        status="completed",
        relationship_="colleague",
        relationship_text="Colleague",
        desired_mood="stylish",
        sender_message="Happy New Year!",
    )
    db_session.add(brief)
    await db_session.flush()

    gen = Generation(
        project_id=project.id,
        type="final",
        status="processing",
        requested_by_user_id=test_user.id,
        input_json={"brief": {}},
    )
    db_session.add(gen)
    await db_session.flush()

    step = GenerationStep(
        generation_id=gen.id,
        step_no=1,
        step_code="script",
        type="text",
        status="processing",
        input_json={"brief": {}},
    )
    db_session.add(step)
    await db_session.commit()

    service = ScriptGenerationService(db_session)
    result = await service.generate_script(
        project_id=project.id,
        owner_user_id=test_user.id,
        generation_step_id=step.id,
    )

    assert result["source"] == "raw_prompt"
    assert result["provider"] == "raw_prompt"
    assert "script" in result
    assert len(result["script"]) > 0


@pytest.mark.asyncio
async def test_script_generation_not_found_project(db_session, test_user):
    from app.core.exceptions import NotFoundException

    gen = Generation(
        project_id=uuid4(),
        type="final",
        status="processing",
        requested_by_user_id=test_user.id,
        input_json={},
    )
    db_session.add(gen)
    await db_session.flush()

    service = ScriptGenerationService(db_session)
    with pytest.raises(NotFoundException):
        await service.generate_script(
            project_id=uuid4(),
            owner_user_id=test_user.id,
            generation_step_id=gen.id,
        )


@pytest.mark.asyncio
async def test_script_generation_not_found_brief(db_session, test_user):
    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="Bob",
        last_name="Jones",
    )
    db_session.add(recipient)
    await db_session.flush()

    project = Project(
        owner_user_id=test_user.id,
        recipient_id=recipient.id,
        title="No Brief Project",
        status="brief_completed",
        occasion_code="birthday",
    )
    db_session.add(project)
    await db_session.flush()

    gen = Generation(
        project_id=project.id,
        type="final",
        status="processing",
        requested_by_user_id=test_user.id,
        input_json={},
    )
    db_session.add(gen)
    await db_session.commit()

    step = GenerationStep(
        generation_id=gen.id,
        step_no=1,
        step_code="script",
        type="text",
        status="processing",
        input_json={},
    )
    db_session.add(step)
    await db_session.commit()

    service = ScriptGenerationService(db_session)
    from app.core.exceptions import NotFoundException

    with pytest.raises(NotFoundException):
        await service.generate_script(
            project_id=project.id,
            owner_user_id=test_user.id,
            generation_step_id=step.id,
        )


@pytest.mark.asyncio
async def test_script_generation_circuit_breaker_opens_on_failures(db_session, test_user):
    from app.services.resilience.circuit_breaker import CircuitState, get_circuit_breaker

    project, _, brief = await _create_project_with_brief(db_session, test_user.id)

    gen = Generation(
        project_id=project.id,
        type="final",
        status="processing",
        requested_by_user_id=test_user.id,
        input_json={},
    )
    db_session.add(gen)
    await db_session.flush()

    cb = get_circuit_breaker("grok_text")
    cb._failures = 5
    cb._state = CircuitState.OPEN

    step = GenerationStep(
        generation_id=gen.id,
        step_no=1,
        step_code="script",
        type="text",
        status="processing",
        input_json={},
    )
    db_session.add(step)
    await db_session.commit()

    service = ScriptGenerationService(db_session)

    template = PromptTemplate(
        code="fallback_birthday_template",
        name="Fallback Birthday Template",
        category="birthday",
        text="Fallback: {base_prompt}",
        variables=["base_prompt"],
        is_active=True,
        success_rate=0.9,
    )
    db_session.add(template)
    await db_session.commit()

    result = await service.generate_script(
        project_id=project.id,
        owner_user_id=test_user.id,
        generation_step_id=step.id,
    )

    assert result["source"] == "fallback_template"
    assert result["provider"] == "cached_template"

    cb._state = CircuitState.CLOSED
    cb._failures = 0


@pytest.mark.asyncio
async def test_script_generation_api_endpoint(client, db_session, test_user):
    """POST /generations/{id}/script endpoint works."""
    project, recipient, brief = await _create_project_with_brief(db_session, test_user.id)

    gen = Generation(
        project_id=project.id,
        type="final",
        status="processing",
        requested_by_user_id=test_user.id,
        input_json={"brief": {}},
    )
    db_session.add(gen)
    await db_session.commit()

    token = create_access_token(test_user.id)
    headers = {"Authorization": f"Bearer {token}", "X-Requested-With": "XMLHttpRequest"}

    response = await client.post(f"/api/v1/generations/{gen.id}/script", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "script" in data
    assert "source" in data


@pytest.mark.asyncio
async def test_script_generation_api_not_found(client, db_session, test_user):
    """POST /generations/{id}/script returns 404 for nonexistent generation."""
    token = create_access_token(test_user.id)
    headers = {"Authorization": f"Bearer {token}", "X-Requested-With": "XMLHttpRequest"}

    response = await client.post(f"/api/v1/generations/{uuid4()}/script", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_script_generation_stores_result_in_step(db_session, test_user):
    project, _, brief = await _create_project_with_brief(db_session, test_user.id)

    gen = Generation(
        project_id=project.id,
        type="final",
        status="processing",
        requested_by_user_id=test_user.id,
        input_json={"brief": {}},
    )
    db_session.add(gen)
    await db_session.flush()

    step = GenerationStep(
        generation_id=gen.id,
        step_no=1,
        step_code="script",
        type="text",
        status="processing",
        input_json={"brief": {}},
    )
    db_session.add(step)
    await db_session.commit()

    service = ScriptGenerationService(db_session)
    result = await service.generate_script(
        project_id=project.id,
        owner_user_id=test_user.id,
        generation_step_id=step.id,
    )

    assert "generated_at" in result
    assert "script" in result
    assert "source" in result
    assert result["script"] is not None
    assert len(result["script"]) > 0
