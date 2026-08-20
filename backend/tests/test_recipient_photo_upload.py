"""Integration tests for recipient photo upload + asset linking flow."""
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models.asset import Asset, StorageObject
from app.models.recipient import Recipient, RecipientAsset


def _fresh_query(stmt):
    return stmt.execution_options(populate_existing=True)


@pytest.mark.asyncio
async def test_photo_upload_url_generates_presigned_url(client, db_session, auth_headers, test_user):
    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="Test",
        last_name="User",
    )
    db_session.add(recipient)
    await db_session.commit()
    await db_session.refresh(recipient)

    response = await client.post(
        f"/api/v1/recipients/{recipient.id}/photo/upload-url",
        json={
            "filename": "photo.jpg",
            "mime_type": "image/jpeg",
            "size_bytes": 1024,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "asset_id" in data
    assert data["upload_url"] == "https://presigned.example.com/upload/abc123"
    assert data["expires_in"] == 900


@pytest.mark.asyncio
async def test_photo_upload_url_rejects_invalid_extension(client, db_session, auth_headers, test_user):
    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="Test",
        last_name="User",
    )
    db_session.add(recipient)
    await db_session.commit()
    await db_session.refresh(recipient)

    response = await client.post(
        f"/api/v1/recipients/{recipient.id}/photo/upload-url",
        json={
            "filename": "document.pdf",
            "mime_type": "application/pdf",
            "size_bytes": 1024,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_photo_upload_url_not_found_for_missing_recipient(client, db_session, auth_headers, test_user):
    missing_id = uuid4()

    response = await client.post(
        f"/api/v1/recipients/{missing_id}/photo/upload-url",
        json={
            "filename": "photo.jpg",
            "mime_type": "image/jpeg",
            "size_bytes": 1024,
        },
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_confirm_photo_upload_creates_asset_and_link(client, db_session, auth_headers, test_user):
    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="Test",
        last_name="User",
    )
    db_session.add(recipient)
    await db_session.commit()
    await db_session.refresh(recipient)

    asset_id = uuid4()
    object_key = f"uploads/{test_user.id}/{asset_id}_photo.jpg"

    response = await client.post(
        f"/api/v1/recipients/{recipient.id}/photo/confirm-upload",
        params={"asset_id": str(asset_id), "object_key": object_key},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "photo_url" in data
    assert data["photo_url"] == f"assets/{asset_id}"

    asset_result = await db_session.execute(_fresh_query(select(Asset).where(Asset.id == asset_id)))
    asset = asset_result.scalar_one()
    assert asset.type == "photo"
    assert asset.owner_user_id == test_user.id

    storage_result = await db_session.execute(_fresh_query(select(StorageObject).where(StorageObject.object_key == object_key)))
    storage_obj = storage_result.scalar_one()
    assert storage_obj is not None

    link_result = await db_session.execute(
        _fresh_query(
            select(RecipientAsset).where(
                RecipientAsset.recipient_id == recipient.id,
                RecipientAsset.asset_id == asset_id,
            )
        )
    )
    link = link_result.scalar_one()
    assert link.is_primary is True
    assert link.sort_order == 0


@pytest.mark.asyncio
async def test_confirm_photo_upload_rejects_wrong_prefix(client, db_session, auth_headers, test_user):
    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="Test",
        last_name="User",
    )
    db_session.add(recipient)
    await db_session.commit()
    await db_session.refresh(recipient)

    asset_id = uuid4()
    object_key = f"uploads/some_other_user/{asset_id}_photo.jpg"

    response = await client.post(
        f"/api/v1/recipients/{recipient.id}/photo/confirm-upload",
        params={"asset_id": str(asset_id), "object_key": object_key},
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_confirm_photo_upload_links_existing_asset(client, db_session, auth_headers, test_user):
    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="Test",
        last_name="User",
    )
    db_session.add(recipient)
    await db_session.commit()
    await db_session.refresh(recipient)

    storage_obj = StorageObject(
        bucket="daragent",
        object_key=f"uploads/{test_user.id}/existing.jpg",
        original_name="existing.jpg",
        mime_type="image/jpeg",
    )
    db_session.add(storage_obj)
    await db_session.commit()
    await db_session.refresh(storage_obj)

    asset = Asset(
        owner_user_id=test_user.id,
        type="photo",
        status="uploaded",
        storage_object_id=storage_obj.id,
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    asset_id = asset.id

    object_key = f"uploads/{test_user.id}/{asset_id}_photo.jpg"

    response = await client.post(
        f"/api/v1/recipients/{recipient.id}/photo/confirm-upload",
        params={"asset_id": str(asset_id), "object_key": object_key},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["photo_url"] is not None

    link_result = await db_session.execute(
        _fresh_query(
            select(RecipientAsset).where(
                RecipientAsset.recipient_id == recipient.id,
                RecipientAsset.asset_id == asset_id,
            )
        )
    )
    link = link_result.scalar_one()
    assert link.is_primary is True


@pytest.mark.asyncio
async def test_confirm_photo_upload_is_idempotent(client, db_session, auth_headers, test_user):
    """Second confirm with the same asset_id should not create a duplicate link."""
    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="Test",
        last_name="User",
    )
    db_session.add(recipient)
    await db_session.commit()
    await db_session.refresh(recipient)

    asset_id = uuid4()
    object_key = f"uploads/{test_user.id}/{asset_id}_photo.jpg"

    response1 = await client.post(
        f"/api/v1/recipients/{recipient.id}/photo/confirm-upload",
        params={"asset_id": str(asset_id), "object_key": object_key},
        headers=auth_headers,
    )
    assert response1.status_code == 200

    response2 = await client.post(
        f"/api/v1/recipients/{recipient.id}/photo/confirm-upload",
        params={"asset_id": str(asset_id), "object_key": object_key},
        headers=auth_headers,
    )
    assert response2.status_code == 200

    link_result = await db_session.execute(
        _fresh_query(
            select(RecipientAsset).where(
                RecipientAsset.recipient_id == recipient.id,
                RecipientAsset.asset_id == asset_id,
            )
        )
    )
    links = link_result.scalars().all()
    assert len(links) == 1


@pytest.mark.asyncio
async def test_get_recipient_includes_photo_url(client, db_session, auth_headers, test_user):
    recipient = Recipient(
        owner_user_id=test_user.id,
        first_name="Test",
        last_name="User",
    )
    db_session.add(recipient)
    await db_session.commit()
    await db_session.refresh(recipient)

    storage_obj = StorageObject(
        bucket="daragent",
        object_key=f"uploads/{test_user.id}/photo.jpg",
        original_name="photo.jpg",
        mime_type="image/jpeg",
    )
    db_session.add(storage_obj)
    await db_session.commit()
    await db_session.refresh(storage_obj)

    asset = Asset(
        owner_user_id=test_user.id,
        type="photo",
        status="uploaded",
        storage_object_id=storage_obj.id,
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)

    link = RecipientAsset(
        recipient_id=recipient.id,
        asset_id=asset.id,
        is_primary=True,
        sort_order=0,
    )
    db_session.add(link)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/recipients/{recipient.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["photo_url"] == f"assets/{asset.id}"
