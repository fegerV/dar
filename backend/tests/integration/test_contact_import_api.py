"""Integration tests for contact import API."""

import io
import json

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestContactImportAPI:
    """Test contact import endpoints."""

    @pytest.mark.asyncio
    async def test_import_json_file(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test importing contacts from JSON file."""
        contacts = [
            {"first_name": "John", "last_name": "Doe", "city": "Moscow"},
            {"first_name": "Jane", "last_name": "Smith", "gender": "female"},
        ]
        json_data = json.dumps(contacts)

        response = await async_client.post(
            "/api/v1/contacts/import",
            files={"file": ("contacts.json", json_data, "application/json")},
            data={"consent_given": "true"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["imported"] == 2
        assert data["skipped"] == 0

    @pytest.mark.asyncio
    async def test_import_csv_file(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test importing contacts from CSV file."""
        csv_content = "first_name,last_name,city\nJohn,Doe,Moscow\nJane,Smith,SPb"

        response = await async_client.post(
            "/api/v1/contacts/import",
            files={"file": ("contacts.csv", csv_content, "text/csv")},
            data={"consent_given": "true"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["imported"] == 2

    @pytest.mark.asyncio
    async def test_import_without_consent(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test that import requires consent."""
        contacts = [{"name": "John"}]
        json_data = json.dumps(contacts)

        response = await async_client.post(
            "/api/v1/contacts/import",
            files={"file": ("contacts.json", json_data, "application/json")},
            data={"consent_given": "false"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_import_with_full_fields(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test importing contacts with all fields."""
        contacts = [
            {
                "first_name": "Alice",
                "last_name": "Wonder",
                "nickname": "Ali",
                "gender": "female",
                "birthday": "1990-01-15",
                "city": "London",
                "occupation": "Engineer",
                "relationship": "friend",
                "phone": "+79001234567",
                "email": "alice@example.com",
                "notes": "Test contact",
                "interests": "AI, ML",
                "traits": "creative",
                "favorites": "coffee",
                "forbidden": "politics",
            }
        ]
        json_data = json.dumps(contacts)

        response = await async_client.post(
            "/api/v1/contacts/import",
            files={"file": ("contacts.json", json_data, "application/json")},
            data={"consent_given": "true"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["imported"] == 1

    @pytest.mark.asyncio
    async def test_import_invalid_file_format(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test that unsupported file formats are rejected."""
        response = await async_client.post(
            "/api/v1/contacts/import",
            files={"file": ("contacts.xml", "<contacts/>", "application/xml")},
            data={"consent_given": "true"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_import_skip_invalid_rows(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test that invalid rows are skipped."""
        contacts = [
            {"first_name": "John"},
            {"city": "Moscow"},
            {"first_name": "Jane"},
        ]
        json_data = json.dumps(contacts)

        response = await async_client.post(
            "/api/v1/contacts/import",
            files={"file": ("contacts.json", json_data, "application/json")},
            data={"consent_given": "true"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["imported"] == 2
        assert data["skipped"] == 1
