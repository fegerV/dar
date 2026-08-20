"""Integration tests for Template Rendering — asset insertion and audio overlay."""
from uuid import uuid4

import pytest

from app.models.asset import Asset, StorageObject
from app.models.template import Scene, Template, TemplateVersion
from app.schemas.template_render import RenderTemplateRequest
from app.services.templates.renderer import TemplateRenderer


async def _create_template_with_scenes(  # noqa: E501
    db_session, test_user, code="birthday_party_v1", render_config=None
):
    template = Template(
        code=code,
        title="Birthday Party Template",
        description="A birthday celebration template",
        kind="video",
        status="published",
        category="birthday",
        occasion_codes=["birthday"],
        relationship_types=["friend", "parent"],
        moods=["funny", "touching"],
        min_price_rub=0,
        base_price_rub=590,
        estimated_duration_sec=30,
    )
    db_session.add(template)
    await db_session.flush()

    version = TemplateVersion(
        template_id=template.id,
        version=1,
        status="published",
        prompt_config={"system_prompt": "You are a helpful assistant", "style": "cinematic"},
        render_config=render_config or {"audio": {"asset_id": None, "volume": 0.8}},
    )
    db_session.add(version)
    await db_session.flush()

    scene = Scene(
        template_id=template.id,
        code="intro",
        title="Intro Scene",
        description="Opening scene",
        duration_sec=10,
        scene_config={
            "prompt_template": "Scene for {{relationship}}",
            "assets": [
                {"asset_id": str(uuid4()), "type": "image"},
                "background_text",
            ],
        },
    )
    db_session.add(scene)
    await db_session.flush()

    return template, version, scene


@pytest.mark.asyncio
async def test_render_resolves_asset_urls(db_session, test_user):
    template, version, scene = await _create_template_with_scenes(db_session, test_user)

    storage_obj = StorageObject(
        bucket="daragent",
        object_key=f"uploads/{test_user.id}/{uuid4()}_photo.png",
        mime_type="image/png",
        width=1024,
        height=768,
    )
    db_session.add(storage_obj)
    await db_session.flush()

    asset = Asset(
        owner_user_id=test_user.id,
        type="image",
        status="uploaded",
        storage_object_id=storage_obj.id,
        mime_type="image/png",
        width=1024,
        height=768,
    )
    db_session.add(asset)
    await db_session.flush()

    scene_config = dict(scene.scene_config)
    scene_config["assets"] = [
        {"asset_id": str(asset.id), "type": "image"},
    ]
    scene.scene_config = scene_config
    await db_session.commit()

    body = RenderTemplateRequest(
        template_version_id=version.id,
        variables={"relationship": "friend"},
    )

    renderer = TemplateRenderer(db_session)
    result = await renderer.render_template(body, fallback_to_cache=False)

    assert len(result.scenes) == 1
    rendered_scene = result.scenes[0]
    assert len(rendered_scene.rendered_assets) == 1
    assert rendered_scene.rendered_assets[0].asset_id == asset.id
    assert rendered_scene.rendered_assets[0].type == "image"
    assert rendered_scene.rendered_assets[0].width == 1024
    assert rendered_scene.rendered_assets[0].height == 768
    assert rendered_scene.rendered_assets[0].mime_type == "image/png"


@pytest.mark.asyncio
async def test_render_preserves_static_assets(db_session, test_user):
    template, version, scene = await _create_template_with_scenes(
        db_session, test_user, code="static_assets_v1"
    )

    body = RenderTemplateRequest(
        template_version_id=version.id,
        variables={"relationship": "friend"},
    )

    renderer = TemplateRenderer(db_session)
    result = await renderer.render_template(body, fallback_to_cache=False)

    rendered_scene = result.scenes[0]
    assert len(rendered_scene.rendered_assets) == 2
    assert rendered_scene.rendered_assets[0].asset_id is not None
    assert rendered_scene.rendered_assets[0].url is None
    assert rendered_scene.rendered_assets[1].type == "text"
    assert rendered_scene.rendered_assets[1].url == "background_text"


@pytest.mark.asyncio
async def test_render_audio_overlay_from_render_config(db_session, test_user):
    template, version, scene = await _create_template_with_scenes(
        db_session, test_user, code="audio_render_v1"
    )

    version.render_config = {
        "audio": {
            "volume": 0.9,
            "offset_sec": 0.5,
        }
    }
    await db_session.commit()

    body = RenderTemplateRequest(
        template_version_id=version.id,
        variables={},
    )

    renderer = TemplateRenderer(db_session)
    result = await renderer.render_template(body, fallback_to_cache=False)

    assert result.audio_overlay is not None
    assert result.audio_overlay.volume == 0.9
    assert result.audio_overlay.offset_sec == 0.5


@pytest.mark.asyncio
async def test_render_audio_overlay_from_scene_config(db_session, test_user):
    template = Template(
        code="birthday_audio_v1",
        title="Birthday with Audio",
        kind="video",
        status="published",
        category="birthday",
    )
    db_session.add(template)
    await db_session.flush()

    version = TemplateVersion(
        template_id=template.id,
        version=1,
        status="published",
        prompt_config={"system_prompt": ""},
        render_config={},
    )
    db_session.add(version)
    await db_session.flush()

    scene = Scene(
        template_id=template.id,
        code="main",
        title="Main Scene",
        duration_sec=15,
        scene_config={
            "prompt_template": "Test scene",
            "assets": [],
            "audio": {"asset_id": str(uuid4()), "volume": 0.7, "offset_sec": 2.0},
        },
    )
    db_session.add(scene)
    await db_session.flush()

    body = RenderTemplateRequest(template_version_id=version.id, variables={})

    renderer = TemplateRenderer(db_session)
    result = await renderer.render_template(body, fallback_to_cache=False)

    assert len(result.scenes) == 1
    assert result.scenes[0].audio_overlay is not None
    assert result.scenes[0].audio_overlay.volume == 0.7
    assert result.scenes[0].audio_overlay.offset_sec == 2.0


@pytest.mark.asyncio
async def test_render_audio_overlay_with_asset_url(db_session, test_user):
    template = Template(
        code="birthday_audio_asset",
        title="Birthday with Audio Asset",
        kind="video",
        status="published",
        category="birthday",
    )
    db_session.add(template)
    await db_session.flush()

    version = TemplateVersion(
        template_id=template.id,
        version=1,
        status="published",
        prompt_config={"system_prompt": ""},
        render_config={},
    )
    db_session.add(version)
    await db_session.flush()

    storage_obj = StorageObject(
        bucket="daragent",
        object_key=f"uploads/{test_user.id}/{uuid4()}_voice.mp3",
        mime_type="audio/mp3",
    )
    db_session.add(storage_obj)
    await db_session.flush()

    asset = Asset(
        owner_user_id=test_user.id,
        type="audio",
        status="uploaded",
        storage_object_id=storage_obj.id,
        mime_type="audio/mp3",
    )
    db_session.add(asset)
    await db_session.flush()

    scene = Scene(
        template_id=template.id,
        code="main",
        title="Main Scene",
        duration_sec=15,
        scene_config={
            "prompt_template": "Test scene",
            "assets": [],
            "audio": {"asset_id": str(asset.id), "volume": 1.0},
        },
    )
    db_session.add(scene)
    await db_session.flush()

    body = RenderTemplateRequest(template_version_id=version.id, variables={})

    renderer = TemplateRenderer(db_session)
    result = await renderer.render_template(body, fallback_to_cache=False)

    assert result.scenes[0].audio_overlay is not None
    assert result.scenes[0].audio_overlay.asset_id == asset.id
    assert result.scenes[0].audio_overlay.volume == 1.0


@pytest.mark.asyncio
async def test_render_audio_overlay_string_url(db_session, test_user):
    template = Template(
        code="birthday_audio_str",
        title="Birthday with String Audio URL",
        kind="video",
        status="published",
        category="birthday",
    )
    db_session.add(template)
    await db_session.flush()

    version = TemplateVersion(
        template_id=template.id,
        version=1,
        status="published",
        prompt_config={},
        render_config={"audio": "https://example.com/music.mp3"},
    )
    db_session.add(version)
    await db_session.flush()

    scene = Scene(
        template_id=template.id,
        code="main",
        title="Main",
        duration_sec=15,
        scene_config={"prompt_template": "test"},
    )
    db_session.add(scene)
    await db_session.flush()

    body = RenderTemplateRequest(template_version_id=version.id, variables={})

    renderer = TemplateRenderer(db_session)
    result = await renderer.render_template(body, fallback_to_cache=False)

    assert result.audio_overlay is not None
    assert result.audio_overlay.url == "https://example.com/music.mp3"


@pytest.mark.asyncio
async def test_render_missing_template_raises(db_session, test_user):
    body = RenderTemplateRequest(
        template_version_id=uuid4(),
        variables={},
    )

    renderer = TemplateRenderer(db_session)
    with pytest.raises(Exception):
        await renderer.render_template(body, fallback_to_cache=False)
