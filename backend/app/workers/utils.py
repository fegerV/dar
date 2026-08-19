import io
from datetime import datetime
from uuid import UUID

from app.integrations.storage.factory import get_storage_provider
from app.models.generation import Generation, GenerationStep


def estimate_eta(steps: list[GenerationStep], current_idx: int) -> int | None:
    completed = [s for s in steps[: current_idx + 1] if s.started_at and s.completed_at]
    if not completed:
        return None
    durations = [(s.completed_at - s.started_at).total_seconds() for s in completed]
    avg = sum(durations) / len(durations)
    remaining = len(steps) - (current_idx + 1)
    return int(avg * remaining)


async def upload_placeholder_video(generation: Generation) -> dict:
    storage = get_storage_provider()
    object_key = f"outputs/{generation.project_id}/{generation.id}/final.mp4"
    thumb_key = f"outputs/{generation.project_id}/{generation.id}/thumb.jpg"

    placeholder_video = b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41"
    placeholder_thumb = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"

    await storage.upload(
        bucket="daragent",
        object_key=object_key,
        data=io.BytesIO(placeholder_video),
        content_type="video/mp4",
    )
    await storage.upload(
        bucket="daragent",
        object_key=thumb_key,
        data=io.BytesIO(placeholder_thumb),
        content_type="image/jpeg",
    )

    video_url = await storage.generate_presigned_url(
        bucket="daragent",
        object_key=object_key,
        expires_in=3600,
    )
    thumbnail_url = await storage.generate_presigned_url(
        bucket="daragent",
        object_key=thumb_key,
        expires_in=3600,
    )

    return {
        "video_url": video_url,
        "thumbnail_url": thumbnail_url,
    }
