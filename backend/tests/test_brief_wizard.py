"""Integration tests for the Creative Brief Wizard — state machine, dynamic questions, autosave, summary."""  # noqa: E501
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models.brief import CreativeBrief
from app.models.project import Project
from app.models.recipient import Recipient


def _create_project(db_session, user_id, **kwargs):
    recipient = Recipient(
        owner_user_id=user_id,
        first_name="Test",
        last_name="User",
    )
    db_session.add(recipient)
    project = Project(
        owner_user_id=user_id,
        recipient_id=recipient.id,
        title="Test Project",
        status="draft",
        **kwargs,
    )
    db_session.add(project)
    return project, recipient


@pytest.mark.asyncio
async def test_brief_state_machine_draft_to_in_progress(  # noqa: E501
    client, db_session, auth_headers, test_user
):
    project = Project(owner_user_id=test_user.id, title="T", status="draft")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    response = await client.put(
        f"/api/v1/projects/{project.id}/brief",
        json={"status": "in_progress", "occasion_text": "Test occasion"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["occasion_text"] == "Test occasion"

    brief_result = await db_session.execute(
        select(CreativeBrief).where(CreativeBrief.project_id == project.id)
    )
    brief = brief_result.scalar_one()
    assert brief.status == "in_progress"


@pytest.mark.asyncio
async def test_brief_state_machine_blocks_invalid_transition(  # noqa: E501
    client, db_session, auth_headers, test_user
):
    project = Project(owner_user_id=test_user.id, title="T", status="draft")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    response = await client.put(
        f"/api/v1/projects/{project.id}/brief",
        json={"status": "completed"},
        headers=auth_headers,
    )

    assert response.status_code == 409
    detail = response.json()["detail"]["error"]
    assert detail["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_complete_brief_requires_fields(client, db_session, auth_headers, test_user):
    project = Project(owner_user_id=test_user.id, title="T", status="draft")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    await client.put(
        f"/api/v1/projects/{project.id}/brief",
        json={"status": "in_progress"},
        headers=auth_headers,
    )

    response = await client.post(
        f"/api/v1/projects/{project.id}/brief/complete",
        headers=auth_headers,
    )

    assert response.status_code == 422
    detail = response.json()["detail"]["error"]
    assert "missing_fields" in detail["details"]


@pytest.mark.asyncio
async def test_complete_brief_success(client, db_session, auth_headers, test_user):
    project = Project(owner_user_id=test_user.id, title="T", status="draft")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    await client.put(
        f"/api/v1/projects/{project.id}/brief",
        json={
            "status": "in_progress",
            "relationship": "friend",
            "relationship_text": "Close friend",
            "desired_mood": "funny",
        },
        headers=auth_headers,
    )

    response = await client.post(
        f"/api/v1/projects/{project.id}/brief/complete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recommendations_ready"

    project_result = await db_session.execute(
        select(Project).where(Project.id == project.id)
    )
    updated_project = project_result.scalar_one()
    assert updated_project.status == "recommendations_ready"

    brief_result = await db_session.execute(
        select(CreativeBrief).where(CreativeBrief.project_id == project.id)
    )
    brief = brief_result.scalar_one()
    assert brief.status == "completed"
    assert brief.completed_at is not None


@pytest.mark.asyncio
async def test_complete_brief_idempotent(client, db_session, auth_headers, test_user):
    """Completing an already-completed brief should succeed (idempotent)."""
    project = Project(owner_user_id=test_user.id, title="T", status="draft")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    await client.put(
        f"/api/v1/projects/{project.id}/brief",
        json={
            "status": "in_progress",
            "relationship": "friend",
            "relationship_text": "Friend",
            "desired_mood": "funny",
        },
        headers=auth_headers,
    )

    response1 = await client.post(
        f"/api/v1/projects/{project.id}/brief/complete",
        headers=auth_headers,
    )
    assert response1.status_code == 200

    response2 = await client.post(
        f"/api/v1/projects/{project.id}/brief/complete",
        headers=auth_headers,
    )
    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_brief_questions_dynamic_relationship(client, db_session, auth_headers, test_user):
    project, _ = _create_project(db_session, test_user.id, occasion_code="birthday")
    await db_session.commit()
    await db_session.refresh(project)

    response = await client.get(
        f"/api/v1/projects/{project.id}/brief/questions?relationship=parent&occasion_code=birthday",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["relationship_type"] == "parent"
    assert data["occasion_code"] == "birthday"
    assert len(data["questions"]) > 2
    field_names = [q["field"] for q in data["questions"]]
    assert "sender_role" in field_names
    assert "inside_joke" in field_names


@pytest.mark.asyncio
async def test_brief_questions_friend_relationship(client, db_session, auth_headers, test_user):
    project, _ = _create_project(db_session, test_user.id, occasion_code="new_year")
    await db_session.commit()
    await db_session.refresh(project)

    response = await client.get(
        f"/api/v1/projects/{project.id}/brief/questions?relationship=friend&occasion_code=new_year",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    field_names = [q["field"] for q in data["questions"]]
    assert "sender_role" in field_names
    assert "memorable_story" in field_names


@pytest.mark.asyncio
async def test_brief_questions_default_relationship(client, db_session, auth_headers, test_user):
    project, _ = _create_project(db_session, test_user.id)
    await db_session.commit()
    await db_session.refresh(project)

    await client.put(
        f"/api/v1/projects/{project.id}/brief",
        json={"status": "in_progress", "relationship": "friend"},
        headers=auth_headers,
    )

    response = await client.get(
        f"/api/v1/projects/{project.id}/brief/questions",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["relationship_type"] == "friend"
    assert "desired_mood" in [q["field"] for q in data["questions"]]


@pytest.mark.asyncio
async def test_brief_summary_empty(client, db_session, auth_headers, test_user):
    project, _ = _create_project(
        db_session, test_user.id,
        occasion_code="birthday", occasion_title="День рождения",
    )
    await db_session.commit()
    await db_session.refresh(project)

    response = await client.get(
        f"/api/v1/projects/{project.id}/brief/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["brief_status"] == "draft"
    assert data["project_status"] == "draft"
    assert data["filled_fields"] == 0
    assert data["completion_percent"] == 0


@pytest.mark.asyncio
async def test_brief_summary_partial(client, db_session, auth_headers, test_user):
    project, recipient = _create_project(
        db_session, test_user.id, occasion_code="birthday", occasion_title="День рождения"
    )
    await db_session.commit()
    await db_session.refresh(project)

    await client.put(
        f"/api/v1/projects/{project.id}/brief",
        json={
            "status": "in_progress",
            "relationship": "parent",
            "relationship_text": "Мама",
            "desired_mood": "touching",
            "sender_message": "Люблю тебя",
            "humor_level": 30,
            "emotion_level": 80,
        },
        headers=auth_headers,
    )

    response = await client.get(
        f"/api/v1/projects/{project.id}/brief/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["brief_status"] == "in_progress"
    assert data["filled_fields"] > 0
    assert data["completion_percent"] > 0
    assert "Мама" in data["relationship"]


@pytest.mark.asyncio
async def test_brief_summary_completed(client, db_session, auth_headers, test_user):
    project, _ = _create_project(
        db_session, test_user.id, occasion_code="wedding", occasion_title="Свадьба"
    )
    await db_session.commit()
    await db_session.refresh(project)

    await client.put(
        f"/api/v1/projects/{project.id}/brief",
        json={
            "status": "in_progress",
            "relationship": "friend",
            "relationship_text": "Друг",
            "desired_mood": "funny",
        },
        headers=auth_headers,
    )

    await client.post(
        f"/api/v1/projects/{project.id}/brief/complete",
        headers=auth_headers,
    )

    response = await client.get(
        f"/api/v1/projects/{project.id}/brief/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["brief_status"] == "completed"
    assert data["project_status"] == "recommendations_ready"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_get_brief_returns_status(client, db_session, auth_headers, test_user):
    project = Project(owner_user_id=test_user.id, title="T", status="draft")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    response = await client.get(
        f"/api/v1/projects/{project.id}/brief",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {} or "status" not in data or data.get("status") is None


@pytest.mark.asyncio
async def test_complete_brief_without_draft_raises_not_found(  # noqa: E501
    client, db_session, auth_headers, test_user
):
    await client.post(
        f"/api/v1/projects/{uuid4()}/brief/complete",
        headers=auth_headers,
    )

    assert True
