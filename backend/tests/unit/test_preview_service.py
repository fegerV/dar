"""Tests for preview generation service."""

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.preview.service import PreviewGenerationService


class TestPreviewGenerationService:
    def test_init(self):
        service = PreviewGenerationService()
        assert service.ffmpeg_path == "ffmpeg"
        assert service.ffprobe_path == "ffprobe"

    @pytest.mark.asyncio
    async def test_generate_preview_no_ffmpeg(self):
        service = PreviewGenerationService()
        with patch.dict("os.environ", {"FFMPEG_PATH": "ffmpeg"}):
            with patch("builtins.__import__", side_effect=ImportError):
                result = await service.generate_preview(
                    "http://example.com/video.mp4",
                    project_id="12345678-1234-5678-1234-567812345678",
                    generation_id="12345678-1234-5678-1234-567812345678",
                )
                assert result["preview_url"] is None

    @pytest.mark.asyncio
    async def test_download_video_success(self):
        service = PreviewGenerationService()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(b"fake video data")
            temp_path = f.name

        try:
            with patch.object(service, "_sync_download") as mock_download:
                mock_download.return_value = None
                await service._download_video("http://example.com/video.mp4", temp_path)
                mock_download.assert_called_once()
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_process_video_success(self):
        service = PreviewGenerationService()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            input_path = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            output_path = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            thumb_path = f.name

        try:
            with patch.object(service, "_sync_process") as mock_process:
                mock_process.return_value = None
                await service._process_video(input_path, output_path, thumb_path)
                mock_process.assert_called_once()
        finally:
            for path in [input_path, output_path, thumb_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_get_watermark_position(self):
        service = PreviewGenerationService()

        x, y = service._get_watermark_position("top-left", 10)
        assert x == "10"
        assert y == "10"

        x, y = service._get_watermark_position("bottom-right", 15)
        assert "w-text_w" in x
        assert "h-text_h" in y

        x, y = service._get_watermark_position("center", 0)
        assert "(w-text_w)/2" in x
        assert "(h-text_h)/2" in y

    def test_get_watermark_position_default(self):
        service = PreviewGenerationService()
        x, y = service._get_watermark_position("unknown", 10)
        assert "w-text_w" in x
