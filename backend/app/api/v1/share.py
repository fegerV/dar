from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ValidationException
from app.schemas.delivery import PublicShareView
from app.services.delivery.service import DeliveryService
from app.services.referrals.service import ReferralService

router = APIRouter(prefix="/share", tags=["Public Share"])


@router.get("/{token}", response_model=PublicShareView)
async def get_public_share(
    token: str,
    ref: str | None = Query(default=None, description="Referral code for attribution"),
    password: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    if ref:
        ref_service = ReferralService(db)
        code_obj = await ref_service.repo.get_by_code(ref)
        if code_obj:
            await DeliveryService(db).repo.track_referral_view_by_code(token, ref)
        else:
            raise ValidationException("Invalid referral code")

    service = DeliveryService(db)
    return await service.get_public_share(token, password)


@router.get("/{token}/embed", response_class=HTMLResponse)
async def get_share_embed(
    token: str,
    ref: str | None = Query(default=None),
    password: str | None = Query(default=None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """HTML page with Open Graph and Twitter Card metadata for social sharing."""
    service = DeliveryService(db)
    view = await service.get_public_share(token, password)

    base_url = str(request.base_url) if request else ""
    share_url = f"{base_url}/share/{token}"
    if ref:
        share_url += f"?ref={ref}"

    title = view.title or "Daragent — AI-generated video"
    description = f"Watch this AI-generated video. Duration: {view.duration_sec or 0}s"
    image_url = view.thumbnail_url or f"{base_url}static/daragent_preview.png"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:url" content="{share_url}">
    <meta property="og:type" content="video.movie">
    <meta property="og:video" content="{view.video_url or ''}">
    <meta property="og:video:width" content="1280">
    <meta property="og:video:height" content="720">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image_url}">
</head>
<body>
    <div id="app">
    <script>
        const _d = {PublicShareView.model_dump_json(view)};
        window.SHARE_DATA = JSON.parse(_d.replace(/</g, '\\u003c'));
    </script>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)


@router.get("/{token}/share-links")
async def get_share_links(
    token: str,
    ref: str | None = Query(default=None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Return pre-built share URLs for social platforms."""
    base_url = str(request.base_url) if request else ""
    share_url = f"{base_url}/share/{token}"
    if ref:
        share_url += f"?ref={ref}"

    service = DeliveryService(db)
    view = await service.get_public_share(token, track=False)

    title = view.title or "Check out this AI-generated video!"
    text = "Amazing AI-generated video from Daragent"

    import urllib.parse

    encoded_url = urllib.parse.quote(share_url, safe="")
    encoded_title = urllib.parse.quote(title, safe="")
    encoded_text = urllib.parse.quote(text, safe="")

    links = {
        "telegram": f"https://t.me/share/url?url={encoded_url}&text={encoded_text}",
        "twitter": f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        "whatsapp": f"https://api.whatsapp.com/send?text={encoded_text}%20{encoded_url}",
        "vk": f"https://vk.com/share.php?url={encoded_url}&text={encoded_title}",
        "direct": share_url,
    }

    return JSONResponse(content={"links": links, "video_url": view.video_url})
