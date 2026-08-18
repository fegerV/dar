"""Integration tests for project lifecycle."""
import pytest
from httpx import AsyncClient


class TestProjectLifecycle:
    @pytest.mark.asyncio
    async def test_full_flow(self, client: AsyncClient):
        # 1. Register user
        reg = await client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "display_name": "Test User",
        })
        assert reg.status_code == 201
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create recipient
        recipient = await client.post("/api/v1/recipients", json={
            "first_name": "Иван",
            "last_name": "Петров",
            "relationship_type": "friend",
            "interests": ["кино", "музыка"],
            "traits": ["весёлый"],
        }, headers=headers)
        assert recipient.status_code == 201
        recipient_id = recipient.json()["id"]

        # 3. Create project
        project = await client.post("/api/v1/projects", json={
            "recipient_id": recipient_id,
            "occasion_code": "birthday",
            "title": "День рождения Ивана",
        }, headers=headers)
        assert project.status_code == 201
        project_id = project.json()["id"]
        assert project.json()["status"] == "briefing"

        # 4. Get brief
        brief_get = await client.get(f"/api/v1/projects/{project_id}/brief", headers=headers)
        assert brief_get.status_code == 200
        assert brief_get.json()["project_id"] == project_id

        # 5. Update brief
        brief_update = await client.put(f"/api/v1/projects/{project_id}/brief", json={
            "relationship_type": "friend",
            "desired_mood": "funny",
            "inside_joke": "шутка про кота",
            "personalization_level": 80,
            "hobbies_text": "кино, музыка, игры",
        }, headers=headers)
        assert brief_update.status_code == 200
        assert brief_update.json()["desired_mood"] == "funny"

        # 6. Complete brief -> triggers recommendations
        complete = await client.post(f"/api/v1/projects/{project_id}/brief/complete", headers=headers)
        assert complete.status_code == 200
        assert complete.json()["status"] == "recommendations_ready"

        # 7. List recommendations
        recs = await client.get(f"/api/v1/projects/{project_id}/recommendations", headers=headers)
        assert recs.status_code == 200
        recs_data = recs.json()
        assert len(recs_data) > 0
        assert recs_data[0]["rank"] == 1

        # 8. Select recommendation
        rec_id = recs_data[0]["id"]
        selected = await client.post(
            f"/api/v1/projects/{project_id}/recommendations/{rec_id}/select",
            headers=headers,
        )
        assert selected.status_code == 200
        assert selected.json()["status"] == "template_selected"
        assert selected.json()["selected_template_version_id"] == recs_data[0]["template_version_id"]

        # 9. Get project details after selection
        project_get = await client.get(f"/api/v1/projects/{project_id}", headers=headers)
        assert project_get.status_code == 200
        assert project_get.json()["status"] == "template_selected"

        # 10. List projects
        projects = await client.get("/api/v1/projects", headers=headers)
        assert projects.status_code == 200
        assert len(projects.json()) == 1

    @pytest.mark.asyncio
    async def test_project_ownership_enforced(self, client: AsyncClient):
        # Create first user and project
        reg1 = await client.post("/api/v1/auth/register", json={
            "email": "user1@example.com",
            "password": "password123",
        })
        token1 = reg1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        recipient = await client.post("/api/v1/recipients", json={
            "first_name": "Test",
        }, headers=headers1)
        recipient_id = recipient.json()["id"]

        project = await client.post("/api/v1/projects", json={
            "recipient_id": recipient_id,
            "occasion_code": "birthday",
        }, headers=headers1)
        project_id = project.json()["id"]

        # Create second user
        reg2 = await client.post("/api/v1/auth/register", json={
            "email": "user2@example.com",
            "password": "password123",
        })
        token2 = reg2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Second user should not access first user's project
        response = await client.get(f"/api/v1/projects/{project_id}", headers=headers2)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_project_invalid_recipient(self, client: AsyncClient):
        reg = await client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
        })
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post("/api/v1/projects", json={
            "recipient_id": "00000000-0000-0000-0000-000000000000",
            "occasion_code": "birthday",
        }, headers=headers)
        assert response.status_code == 404
