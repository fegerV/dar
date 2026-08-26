"""Video preview generation service with watermark."""

import asyncio
import logging
import os
import tempfile
from uuid import UUID

from app.core.config import settings
from app.integrations.storage.factory import get_storage_provider

logger = logging.getLogger(__name__)


class PreviewGenerationService:
    """Service for generating watermarked preview videos."""

    def __init__(self):
        self.ffmpeg_path = settings.FFMPEG_PATH
        self.ffprobe_path = settings.FFPROBE_PATH

    async def generate_preview(
        self,
        video_url: str,
        project_id: UUID,
        generation_id: UUID,
    ) -> dict:
        """Generate 360p watermarked preview from source video.

        Returns dict with preview_url and preview_thumbnail_url.
        """
        try:
            import ffmpeg
            _ = ffmpeg
        except ImportError:
            logger.warning("ffmpeg-python not installed, skipping preview generation")
            return {"preview_url": None, "preview_thumbnail_url": None}

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.mp4")
            output_path = os.path.join(tmpdir, "preview_360p.mp4")
            thumb_path = os.path.join(tmpdir, "preview_thumb.jpg")

            await self._download_video(video_url, input_path)

            if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
                logger.warning("Downloaded video is empty for generation %s", generation_id)
                return {"preview_url": None, "preview_thumbnail_url": None}

            await self._process_video(input_path, output_path, thumb_path)

            if not os.path.exists(output_path):
                logger.warning("Preview generation failed for generation %s", generation_id)
                return {"preview_url": None, "preview_thumbnail_url": None}

            storage = get_storage_provider()

            preview_key = f"outputs/{project_id}/{generation_id}/preview_360p.mp4"
            thumb_key = f"outputs/{project_id}/{generation_id}/preview_thumb.jpg"

            with open(output_path, "rb") as f:
                await storage.upload(
                    bucket="daragent",
                    object_key=preview_key,
                    data=f,
                    content_type="video/mp4",
                )

            with open(thumb_path, "rb") as f:
                await storage.upload(
                    bucket="daragent",
                    object_key=thumb_key,
                    data=f,
                    content_type="image/jpeg",
                )

            preview_url = await storage.generate_presigned_url(
                bucket="daragent",
                object_key=preview_key,
                expires_in=3600,
            )
            thumbnail_url = await storage.generate_presigned_url(
                bucket="daragent",
                object_key=thumb_key,
                expires_in=3600,
            )

            return {
                "preview_url": preview_url,
                "preview_thumbnail_url": thumbnail_url,
            }

    async def _download_video(self, url: str, output_path: str):
        """Download video from URL to local path."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, lambda: self._sync_download(url, output_path)
            )
        except Exception as e:
            logger.error("Failed to download video from %s: %s", url, e)

    def _sync_download(self, url: str, output_path: str):
        """Synchronous video download using ffmpeg."""
        import ffmpeg

        try:
            (
                ffmpeg
                .input(url)
                .output(output_path, c="copy", movflags="+faststart")
                .overwrite_output()
                .run(cmd=self.ffmpeg_path, capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            logger.error("ffmpeg download error: %s", e.stderr.decode() if e.stderr else str(e))
            raise

    async def _process_video(self, input_path: str, output_path: str, thumb_path: str):
        """Process video: scale to 360p, add watermark, extract thumbnail."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, lambda: self._sync_process(input_path, output_path, thumb_path)
            )
        except Exception as e:
            logger.error("Failed to process video: %s", e)

    def _sync_process(self, input_path: str, output_path: str, thumb_path: str):
        """Synchronous video processing with ffmpeg."""
        import ffmpeg

        resolution = settings.PREVIEW_RESOLUTION
        watermark_text = settings.PREVIEW_WATERMARK_TEXT
        opacity = settings.PREVIEW_WATERMARK_OPACITY
        position = settings.PREVIEW_WATERMARK_POSITION
        padding = settings.PREVIEW_WATERMARK_PADDING

        self._drawtext_x, self._drawtext_y = self._get_watermark_position(
            position, padding
        )

        try:
            probe = ffmpeg.probe(input_path, cmd=self.ffprobe_path)
            video_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "video"), None
            )

            if not video_stream:
                raise ValueError("No video stream found")

            target_w, target_h = map(int, resolution.split("x"))

            video = ffmpeg.input(input_path).video
            video = video.filter_("scale", target_w, target_h)
            video = video.filter_(
                "drawtext",
                text=watermark_text,
                fontsize="h*0.04",
                fontcolor=f"white@{opacity}",
                box=1,
                boxcolor="black@0.3",
                boxborderw=4,
                x=self._drawtext_x,
                y=self._drawtext_y,
            )

            audio = ffmpeg.input(input_path).audio

            (
                ffmpeg
                .output(
                    video,
                    audio,
                    output_path,
                    vcodec="libx264",
                    acodec="aac",
                    video_bitrate=settings.PREVIEW_BITRATE,
                    crf=settings.PREVIEW_CRF,
                    preset="veryfast",
                    movflags="+faststart",
                    vf=f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2",
                )
                .overwrite_output()
                .run(cmd=self.ffmpeg_path, capture_stdout=True, capture_stderr=True)
            )

            self._extract_thumbnail(input_path, thumb_path)

        except ffmpeg.Error as e:
            logger.error("ffmpeg processing error: %s", e.stderr.decode() if e.stderr else str(e))
            raise

    def _get_watermark_position(self, position: str, padding: int) -> tuple:
        """Get x,y expression for watermark position."""
        positions = {
            "top-left": (f"{padding}", f"{padding}"),
            "top-right": (f"w-text_w-{padding}", f"{padding}"),
            "bottom-left": (f"{padding}", f"h-text_h-{padding}"),
            "bottom-right": (f"w-text_w-{padding}", f"h-text_h-{padding}"),
            "center": ("(w-text_w)/2", "(h-text_h)/2"),
        }
        return positions.get(position, positions["bottom-right"])

    def _extract_thumbnail(self, input_path: str, output_path: str):
        """Extract a thumbnail from the video at 1 second mark."""
        import ffmpeg

        try:
            (
                ffmpeg
                .input(input_path, ss="00:00:01")
                .output(
                    output_path,
                    vframes=1,
                    vf="scale=480:-1",
                    qscale=5,
                )
                .overwrite_output()
                .run(cmd=self.ffmpeg_path, capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error("Thumbnail extraction error: %s", error_msg)


async def generate_preview_for_generation(
    video_url: str,
    project_id: UUID,
    generation_id: UUID,
) -> dict:
    """Convenience function to generate preview for a generation."""
    service = PreviewGenerationService()
    return await service.generate_preview(video_url, project_id, generation_id)
