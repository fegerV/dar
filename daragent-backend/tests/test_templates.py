"""Integration tests for template CRUD and seed data."""
import pytest
from httpx import AsyncClient


class TestTemplates:
    @pytest.mark.asyncio
    async def test_list_templates_seeds_on_first_call(self, client: AsyncClient):
        response = await client.get("/api/v1/templates")
        assert response.status_code == 200
        templates = response.json()
        assert len(templates) == 5
        codes = {t["code"] for t in templates}
        assert "secret_operation_birthday" in codes
        assert "space_captain_anniversary" in codes

    @pytest.mark.asyncio
    async def test_list_templates_idempotent(self, client: AsyncClient):
        await client.get("/api/v1/templates")
        response = await client.get("/api/v1/templates")
        assert response.status_code == 200
        assert len(response.json()) == 5

    @pytest.mark.asyncio
    async def test_get_template_by_id(self, client: AsyncClient):
        list_resp = await client.get("/api/v1/templates")
        templates = list_resp.json()
        template_id = templates[0]["id"]

        response = await client.get(f"/api/v1/templates/{template_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/templates/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_create_template(self, client: AsyncClient):
        # Register and make admin by being first user (already admin)
        reg = await client.post("/api/v1/auth/register", json={
            "email": "admin@example.com",
            "password": "password123",
        })
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post("/api/v1/admin/templates", json={
            "code": "custom_template",
            "title": "Custom Template",
            "description": "Test template",
            "kind": "video",
            "category": "test",
            "occasion_codes": ["birthday"],
            "relationship_types": ["friend"],
            "moods": ["funny"],
            "base_price_rub": 690,
        }, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "custom_template"
        assert data["base_price_rub"] == 690

    @pytest.mark.asyncio
    async def test_admin_list_templates(self, client: AsyncClient):
        reg = await client.post("/api/v1/auth/register", json={
            "email": "admin@example.com",
            "password": "password123",
        })
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/admin/templates", headers=headers)
        assert response.status_code == 200
        templates = response.json()
        assert len(templates) == 5  # seed templates
