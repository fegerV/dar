"""Minimal smoke flow for a running local MVP API.

Usage from `daragent-backend` after starting the service:
    python scripts/smoke_mvp.py
"""

from __future__ import annotations

import time

import httpx

BASE_URL = "http://localhost:8000/api/v1"


def main() -> None:
    email = f"smoke-{int(time.time())}@example.com"
    client = httpx.Client(timeout=20)

    auth = client.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "password": "StrongPassword123!", "display_name": "Smoke"},
    ).raise_for_status().json()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}

    recipient = client.post(
        f"{BASE_URL}/recipients",
        headers=headers,
        json={
            "first_name": "Сергей",
            "relationship_type": "colleague",
            "interests": ["cars", "fishing"],
            "traits": ["funny"],
        },
    ).raise_for_status().json()

    project = client.post(
        f"{BASE_URL}/projects",
        headers=headers,
        json={"recipient_id": recipient["id"], "occasion_code": "birthday", "title": "Поздравление для Сергея"},
    ).raise_for_status().json()

    client.put(
        f"{BASE_URL}/projects/{project['id']}/brief",
        headers=headers,
        json={"desired_mood": "funny", "inside_joke": "пять минут", "humor_level": 90},
    ).raise_for_status()
    client.post(f"{BASE_URL}/projects/{project['id']}/brief/complete", headers=headers).raise_for_status()

    recs = client.get(f"{BASE_URL}/projects/{project['id']}/recommendations", headers=headers).raise_for_status().json()
    client.post(
        f"{BASE_URL}/projects/{project['id']}/recommendations/{recs[0]['id']}/select",
        headers=headers,
    ).raise_for_status()

    asset = client.post(
        f"{BASE_URL}/assets",
        headers=headers,
        json={"type": "photo", "filename": "sender.jpg", "mime_type": "image/jpeg", "size_bytes": 1234},
    ).raise_for_status().json()
    client.post(
        f"{BASE_URL}/projects/{project['id']}/assets",
        headers=headers,
        json={"asset_id": asset["id"], "role": "sender_photo"},
    ).raise_for_status()

    generation = client.post(f"{BASE_URL}/projects/{project['id']}/generate", headers=headers).raise_for_status().json()
    delivery = client.post(
        f"{BASE_URL}/projects/{project['id']}/delivery",
        headers=headers,
        json={"channel": "link"},
    ).raise_for_status().json()

    public = client.get(f"http://localhost:8000{delivery['public_url']}").raise_for_status().json()
    print({"email": email, "generation_status": generation["status"], "share_status": public["status"]})


if __name__ == "__main__":
    main()
