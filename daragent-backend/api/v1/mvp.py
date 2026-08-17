"""Backend-first MVP API.

The implementation is intentionally compact: it establishes the complete
domain flow while keeping room to split services/repositories later.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_providers.router import ai_router
from core.database import get_db
from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    hash_token,
    new_refresh_token,
    token_expiry,
    verify_password,
)
from models import (
    AdminUser,
    AnalyticsEvent,
    Asset,
    AuthAccount,
    CreativeBrief,
    Delivery,
    DeliveryLink,
    Entitlement,
    Feedback,
    Generation,
    GenerationOutput,
    GenerationStep,
    Payment,
    Project,
    ProjectAsset,
    Recipient,
    Recommendation,
    RefreshToken,
    StorageObject,
    Template,
    TemplateVersion,
    User,
    Wallet,
    WalletTransaction,
)

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str | None
    status: str
    is_admin: bool

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: str | None = None
    locale: str | None = None
    timezone: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RecipientIn(BaseModel):
    first_name: str
    last_name: str | None = None
    nickname: str | None = None
    gender: str | None = None
    relationship: str | None = None
    relationship_label: str | None = None
    interests: list[str] = []
    traits: list[str] = []
    forbidden_topics: list[str] = []
    notes: str | None = None


class RecipientResponse(RecipientIn):
    id: uuid.UUID
    status: str

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    recipient_id: uuid.UUID
    occasion_code: str
    occasion_title: str | None = None
    title: str | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    recipient_id: uuid.UUID | None
    title: str | None
    status: str
    occasion_code: str
    occasion_title: str | None
    selected_recommendation_id: uuid.UUID | None
    selected_template_version_id: uuid.UUID | None
    final_generation_id: uuid.UUID | None
    price_rub: Decimal
    paid_rub: Decimal

    model_config = {"from_attributes": True}


class BriefIn(BaseModel):
    relationship: str | None = None
    desired_mood: str | None = None
    desired_length_sec: int | None = Field(default=None, ge=3, le=300)
    humor_level: int | None = Field(default=None, ge=0, le=100)
    emotion_level: int | None = Field(default=None, ge=0, le=100)
    surprise_level: int | None = Field(default=None, ge=0, le=100)
    personalization_level: int | None = Field(default=None, ge=0, le=100)
    inside_joke: str | None = None
    hobbies_text: str | None = None
    character_traits: str | None = None
    memorable_story: str | None = None
    desired_phrase: str | None = None
    forbidden_topics: str | None = None
    sender_message: str | None = None
    selected_options: dict[str, Any] = {}


class BriefResponse(BriefIn):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str

    model_config = {"from_attributes": True}


class TemplateResponse(BaseModel):
    id: uuid.UUID
    code: str
    title: str
    description: str | None
    kind: str
    status: str
    category: str | None
    occasion_codes: list[str]
    relationship_types: list[str]
    moods: list[str]
    base_price_rub: Decimal

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    template_version_id: uuid.UUID
    rank: int
    score: Decimal
    status: str
    match_reasons: list[str]
    explanation: str | None

    model_config = {"from_attributes": True}


class AssetCreate(BaseModel):
    type: str
    filename: str
    mime_type: str
    size_bytes: int | None = None
    url: str | None = None


class AssetResponse(BaseModel):
    id: uuid.UUID
    type: str
    status: str
    mime_type: str | None
    url: str | None

    model_config = {"from_attributes": True}


class AttachAssetRequest(BaseModel):
    asset_id: uuid.UUID
    role: str = "sender_photo"


class PriceResponse(BaseModel):
    base_price_rub: Decimal
    total_rub: Decimal
    currency: str = "RUB"
    free_generation_available: bool


class PaymentCreate(BaseModel):
    method: str = "mock"
    idempotency_key: str | None = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID | None
    status: str
    method: str
    amount_rub: Decimal
    provider: str

    model_config = {"from_attributes": True}


class WalletResponse(BaseModel):
    balance_rub: Decimal
    bonus_balance: Decimal


class WalletTransactionResponse(BaseModel):
    id: uuid.UUID
    type: str
    status: str
    amount_rub: Decimal
    bonus_amount_rub: Decimal
    balance_after_rub: Decimal | None
    description: str | None

    model_config = {"from_attributes": True}


class GenerationResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    type: str
    status: str
    progress: int
    current_step: str | None
    error_code: str | None
    error_message: str | None
    output_assets: list[AssetResponse] = []

    model_config = {"from_attributes": True}


class DeliveryCreate(BaseModel):
    channel: str = "link"
    destination: str | None = None


class DeliveryResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    channel: str
    status: str
    public_url: str | None = None


class FeedbackIn(BaseModel):
    reaction: str
    categories: list[str] = []
    comment: str | None = None


class TemplateCreate(BaseModel):
    code: str
    title: str
    description: str | None = None
    kind: str = "video"
    category: str | None = None
    occasion_codes: list[str] = []
    relationship_types: list[str] = []
    moods: list[str] = []
    base_price_rub: Decimal = Decimal("590")


class AnalyticsIn(BaseModel):
    event_name: str
    project_id: uuid.UUID | None = None
    platform: str | None = None
    properties: dict[str, Any] = {}


async def current_user(
    authorization: str | None = Header(default=None), db: AsyncSession = Depends(get_db)
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    try:
        user_id = decode_access_token(authorization.split(" ", 1)[1])
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    user = await db.get(User, user_id)
    if not user or user.status != "active":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inactive user")
    return user


async def admin_user(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> User:
    admin = await db.scalar(select(AdminUser).where(AdminUser.user_id == user.id, AdminUser.is_active.is_(True)))
    if not user.is_admin and not admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user


async def record_event(db: AsyncSession, name: str, user_id=None, project_id=None, **properties):
    db.add(AnalyticsEvent(user_id=user_id, project_id=project_id, event_name=name, properties=properties))


async def get_owned_project(db: AsyncSession, user: User, project_id: uuid.UUID) -> Project:
    project = await db.get(Project, project_id)
    if not project or project.owner_user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    return project


async def get_project_brief(db: AsyncSession, project_id: uuid.UUID) -> CreativeBrief:
    brief = await db.scalar(select(CreativeBrief).where(CreativeBrief.project_id == project_id))
    if not brief:
        raise HTTPException(404, "Brief not found")
    return brief


async def calculate_price(db: AsyncSession, user: User, project: Project) -> PriceResponse:
    free = await has_entitlement(db, user.id, "first_generation")
    total = Decimal("0") if free else project.price_rub
    return PriceResponse(base_price_rub=project.price_rub, total_rub=total, free_generation_available=free)


def response_generation(gen: Generation, assets: list[Asset] | None = None) -> GenerationResponse:
    return GenerationResponse.model_validate(gen).model_copy(
        update={"output_assets": [AssetResponse.model_validate(asset) for asset in assets or []]}
    )


@router.post("/auth/register", response_model=AuthResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    is_first_user = (await db.scalar(select(func.count()).select_from(User))) == 0
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password), display_name=payload.display_name, is_admin=is_first_user)
    db.add(user)
    await db.flush()
    db.add(AuthAccount(user_id=user.id, provider="email", provider_user_id=user.email))
    db.add(Wallet(user_id=user.id))
    db.add(Entitlement(user_id=user.id, code="first_generation", quantity=1, source="registration"))
    if is_first_user:
        db.add(AdminUser(user_id=user.id, role="owner"))
    refresh, refresh_hash = new_refresh_token()
    db.add(RefreshToken(user_id=user.id, token_hash=refresh_hash, expires_at=token_expiry()))
    await record_event(db, "registration", user_id=user.id)
    return AuthResponse(access_token=create_access_token(user.id), refresh_token=refresh, user=user)


@router.post("/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    refresh, refresh_hash = new_refresh_token()
    db.add(RefreshToken(user_id=user.id, token_hash=refresh_hash, expires_at=token_expiry()))
    await record_event(db, "login", user_id=user.id)
    return AuthResponse(access_token=create_access_token(user.id), refresh_token=refresh, user=user)


@router.post("/auth/refresh")
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_token(payload.refresh_token)
    row = await db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash, RefreshToken.revoked_at.is_(None)))
    if not row:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expires_at = row.expires_at.replace(tzinfo=None) if row.expires_at.tzinfo else row.expires_at
    if expires_at < now:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    return {"access_token": create_access_token(row.user_id), "token_type": "bearer"}


@router.get("/auth/me", response_model=UserResponse)
async def me(user: User = Depends(current_user)):
    return user


@router.patch("/users/me", response_model=UserResponse)
async def update_me(payload: UserUpdate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    return user


@router.get("/recipients", response_model=list[RecipientResponse])
async def list_recipients(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(select(Recipient).where(Recipient.owner_user_id == user.id, Recipient.status != "archived"))
    return list(rows)


@router.post("/recipients", response_model=RecipientResponse, status_code=201)
async def create_recipient(payload: RecipientIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    recipient = Recipient(owner_user_id=user.id, **payload.model_dump())
    db.add(recipient)
    await db.flush()
    await record_event(db, "recipient_created", user_id=user.id)
    return recipient


@router.get("/recipients/{recipient_id}", response_model=RecipientResponse)
async def get_recipient(recipient_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    recipient = await db.get(Recipient, recipient_id)
    if not recipient or recipient.owner_user_id != user.id:
        raise HTTPException(404, "Recipient not found")
    return recipient


@router.patch("/recipients/{recipient_id}", response_model=RecipientResponse)
async def update_recipient(recipient_id: uuid.UUID, payload: RecipientIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    recipient = await get_recipient(recipient_id, user, db)
    for key, value in payload.model_dump().items():
        setattr(recipient, key, value)
    return recipient


@router.delete("/recipients/{recipient_id}", status_code=204)
async def delete_recipient(recipient_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    recipient = await get_recipient(recipient_id, user, db)
    recipient.status = "archived"


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(payload: ProjectCreate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    recipient = await db.get(Recipient, payload.recipient_id)
    if not recipient or recipient.owner_user_id != user.id:
        raise HTTPException(404, "Recipient not found")
    project = Project(owner_user_id=user.id, **payload.model_dump())
    db.add(project)
    await db.flush()
    db.add(CreativeBrief(project_id=project.id, relationship=recipient.relationship))
    await record_event(db, "project_created", user_id=user.id, project_id=project.id)
    return project


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(select(Project).where(Project.owner_user_id == user.id).order_by(Project.created_at.desc()))
    return list(rows)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await get_owned_project(db, user, project_id)


@router.get("/projects/{project_id}/brief", response_model=BriefResponse)
async def get_brief(project_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await get_owned_project(db, user, project_id)
    return await get_project_brief(db, project_id)


@router.put("/projects/{project_id}/brief", response_model=BriefResponse)
async def update_brief(project_id: uuid.UUID, payload: BriefIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await get_owned_project(db, user, project_id)
    brief = await get_project_brief(db, project_id)
    for key, value in payload.model_dump().items():
        setattr(brief, key, value)
    return brief


@router.post("/projects/{project_id}/brief/complete")
async def complete_brief(project_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    project = await get_owned_project(db, user, project_id)
    brief = await get_project_brief(db, project_id)
    if not brief.desired_mood:
        raise HTTPException(422, "desired_mood is required")
    brief.status = "completed"
    project.status = "briefing"
    await generate_recommendations_for_project(db, project, brief)
    project.status = "recommended"
    await record_event(db, "brief_completed", user_id=user.id, project_id=project.id)
    return {"project_id": project.id, "status": "recommendations_ready"}


@router.get("/templates", response_model=list[TemplateResponse])
async def list_templates(db: AsyncSession = Depends(get_db)):
    await seed_templates(db)
    rows = await db.scalars(select(Template).where(Template.status == "active"))
    return list(rows)


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    template = await db.get(Template, template_id)
    if not template or template.status != "active":
        raise HTTPException(404, "Template not found")
    return template


@router.get("/projects/{project_id}/recommendations", response_model=list[RecommendationResponse])
async def list_recommendations(project_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await get_owned_project(db, user, project_id)
    rows = await db.scalars(select(Recommendation).where(Recommendation.project_id == project_id).order_by(Recommendation.rank))
    return list(rows)


@router.post("/projects/{project_id}/recommendations/{recommendation_id}/select", response_model=ProjectResponse)
async def select_recommendation(project_id: uuid.UUID, recommendation_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    project = await get_owned_project(db, user, project_id)
    rec = await db.get(Recommendation, recommendation_id)
    if not rec or rec.project_id != project.id:
        raise HTTPException(404, "Recommendation not found")
    project.selected_recommendation_id = rec.id
    project.selected_template_version_id = rec.template_version_id
    rec.status = "selected"
    project.status = "template_selected"
    template_version = await db.get(TemplateVersion, rec.template_version_id)
    template = await db.get(Template, template_version.template_id)
    project.price_rub = template.base_price_rub
    await record_event(db, "template_selected", user_id=user.id, project_id=project.id, recommendation_id=str(rec.id))
    return project


@router.post("/assets", response_model=AssetResponse, status_code=201)
async def create_asset(payload: AssetCreate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    key = f"users/{user.id}/{uuid.uuid4()}-{payload.filename}"
    storage = StorageObject(bucket="daragent", object_key=key, mime_type=payload.mime_type, size_bytes=payload.size_bytes)
    db.add(storage)
    await db.flush()
    asset = Asset(owner_user_id=user.id, type=payload.type, storage_object_id=storage.id, title=payload.filename, mime_type=payload.mime_type, url=payload.url or f"mock://{key}")
    db.add(asset)
    await db.flush()
    await record_event(db, "asset_uploaded", user_id=user.id)
    return asset


@router.post("/projects/{project_id}/assets", response_model=AssetResponse, status_code=201)
async def attach_asset(project_id: uuid.UUID, payload: AttachAssetRequest, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await get_owned_project(db, user, project_id)
    asset = await db.get(Asset, payload.asset_id)
    if not asset or asset.owner_user_id != user.id:
        raise HTTPException(404, "Asset not found")
    db.add(ProjectAsset(project_id=project_id, asset_id=asset.id, role=payload.role))
    await record_event(db, "asset_attached", user_id=user.id, project_id=project_id, role=payload.role)
    return asset


@router.get("/projects/{project_id}/price", response_model=PriceResponse)
async def get_price(project_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    project = await get_owned_project(db, user, project_id)
    return await calculate_price(db, user, project)


@router.post("/projects/{project_id}/payment", response_model=PaymentResponse, status_code=201)
async def create_payment(project_id: uuid.UUID, payload: PaymentCreate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    project = await get_owned_project(db, user, project_id)
    price = await calculate_price(db, user, project)
    payment = Payment(
        user_id=user.id,
        project_id=project.id,
        provider="mock",
        method=payload.method,
        status="paid" if price.total_rub == 0 else "pending",
        amount_rub=price.total_rub,
        external_payment_id=f"mock_{uuid.uuid4()}",
        idempotency_key=payload.idempotency_key,
        paid_at=datetime.now(timezone.utc) if price.total_rub == 0 else None,
    )
    db.add(payment)
    if payment.status == "paid":
        project.paid_rub = price.total_rub
        project.status = "paid"
    await record_event(db, "payment_created", user_id=user.id, project_id=project.id, amount=str(price.total_rub))
    return payment


@router.post("/payments/mock/{payment_id}/succeed", response_model=PaymentResponse)
async def mock_payment_succeed(payment_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    payment = await db.get(Payment, payment_id)
    if not payment or payment.user_id != user.id:
        raise HTTPException(404, "Payment not found")
    if payment.status != "paid":
        payment.status = "paid"
        payment.paid_at = datetime.now(timezone.utc)
        project = await db.get(Project, payment.project_id)
        if project:
            project.paid_rub = payment.amount_rub
            project.status = "paid"
        await record_event(db, "payment_succeeded", user_id=user.id, project_id=payment.project_id, amount=str(payment.amount_rub))
    return payment


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    payment = await db.get(Payment, payment_id)
    if not payment or payment.user_id != user.id:
        raise HTTPException(404, "Payment not found")
    return payment


@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    wallet = await db.scalar(select(Wallet).where(Wallet.user_id == user.id))
    if not wallet:
        raise HTTPException(404, "Wallet not found")
    return WalletResponse(balance_rub=wallet.balance_rub, bonus_balance=wallet.bonus_balance)


@router.get("/wallet/transactions", response_model=list[WalletTransactionResponse])
async def list_wallet_transactions(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    wallet = await db.scalar(select(Wallet).where(Wallet.user_id == user.id))
    if not wallet:
        raise HTTPException(404, "Wallet not found")
    rows = await db.scalars(select(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id).order_by(WalletTransaction.created_at.desc()))
    return list(rows)


@router.post("/projects/{project_id}/generate", response_model=GenerationResponse, status_code=202)
async def start_generation(project_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    project = await get_owned_project(db, user, project_id)
    await validate_project_ready(db, user, project)
    if project.paid_rub <= 0:
        await consume_entitlement(db, user.id, "first_generation", project.id)
    generation = Generation(project_id=project.id, template_version_id=project.selected_template_version_id, status="queued", progress=0)
    db.add(generation)
    await db.flush()
    project.final_generation_id = generation.id
    project.status = "queued"
    await run_mock_generation(db, generation, project)
    await record_event(db, "generation_started", user_id=user.id, project_id=project.id)
    assets = await generation_assets(db, generation.id)
    return response_generation(generation, assets)


@router.get("/projects/{project_id}/generation", response_model=GenerationResponse)
async def get_project_generation(project_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    project = await get_owned_project(db, user, project_id)
    if not project.final_generation_id:
        raise HTTPException(404, "Generation not found")
    generation = await db.get(Generation, project.final_generation_id)
    return response_generation(generation, await generation_assets(db, generation.id))


@router.get("/generations/{generation_id}", response_model=GenerationResponse)
async def get_generation(generation_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    generation = await db.get(Generation, generation_id)
    if not generation:
        raise HTTPException(404, "Generation not found")
    project = await get_owned_project(db, user, generation.project_id)
    return response_generation(generation, await generation_assets(db, generation.id))


@router.post("/generations/{generation_id}/cancel", response_model=GenerationResponse)
async def cancel_generation(generation_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    generation = await db.get(Generation, generation_id)
    if not generation:
        raise HTTPException(404, "Generation not found")
    await get_owned_project(db, user, generation.project_id)
    if generation.status in {"completed", "failed"}:
        raise HTTPException(409, "Generation cannot be cancelled")
    generation.status = "cancelled"
    generation.current_step = None
    return response_generation(generation, await generation_assets(db, generation.id))


@router.post("/projects/{project_id}/delivery", response_model=DeliveryResponse, status_code=201)
async def create_delivery(project_id: uuid.UUID, payload: DeliveryCreate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    project = await get_owned_project(db, user, project_id)
    if project.status != "ready" or not project.final_generation_id:
        raise HTTPException(409, "Project is not ready")
    token = secrets.token_urlsafe(24)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    link = DeliveryLink(project_id=project.id, generation_id=project.final_generation_id, token_hash=token_hash)
    db.add(link)
    await db.flush()
    delivery = Delivery(project_id=project.id, generation_id=project.final_generation_id, user_id=user.id, channel=payload.channel, destination=payload.destination, delivery_link_id=link.id, status="sent")
    db.add(delivery)
    await record_event(db, "delivery_created", user_id=user.id, project_id=project.id, channel=payload.channel)
    return DeliveryResponse(id=delivery.id, project_id=project.id, channel=delivery.channel, status=delivery.status, public_url=f"/api/v1/share/{token}")


@router.get("/projects/{project_id}/deliveries", response_model=list[DeliveryResponse])
async def list_deliveries(project_id: uuid.UUID, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await get_owned_project(db, user, project_id)
    rows = await db.scalars(select(Delivery).where(Delivery.project_id == project_id).order_by(Delivery.created_at.desc()))
    result = []
    for delivery in rows:
        result.append(DeliveryResponse(id=delivery.id, project_id=delivery.project_id, channel=delivery.channel, status=delivery.status, public_url=None))
    return result


@router.get("/share/{token}")
async def open_share(token: str, db: AsyncSession = Depends(get_db)):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    link = await db.scalar(select(DeliveryLink).where(DeliveryLink.token_hash == token_hash, DeliveryLink.is_active.is_(True)))
    if not link:
        raise HTTPException(404, "Greeting not found")
    link.view_count += 1
    link.last_opened_at = datetime.now(timezone.utc)
    project = await db.get(Project, link.project_id)
    recipient = await db.get(Recipient, project.recipient_id) if project and project.recipient_id else None
    generation = await db.get(Generation, link.generation_id) if link.generation_id else None
    assets = await generation_assets(db, generation.id) if generation else []
    video = assets[0] if assets else None
    await record_event(db, "share_opened", project_id=project.id if project else None)
    return {
        "project_id": project.id,
        "title": project.title,
        "recipient_name": recipient.nickname or recipient.first_name if recipient else None,
        "status": project.status,
        "video_url": video.url if video else None,
        "reply_cta": "Ответить своим поздравлением",
    }


@router.post("/share/{token}/feedback")
async def share_feedback(token: str, payload: FeedbackIn, db: AsyncSession = Depends(get_db)):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    link = await db.scalar(select(DeliveryLink).where(DeliveryLink.token_hash == token_hash, DeliveryLink.is_active.is_(True)))
    if not link:
        raise HTTPException(404, "Greeting not found")
    feedback = Feedback(project_id=link.project_id, generation_id=link.generation_id, reaction=payload.reaction, categories=payload.categories, comment=payload.comment)
    db.add(feedback)
    await record_event(db, "feedback_submitted", project_id=link.project_id, reaction=payload.reaction)
    return {"received": True}


@router.post("/feedback")
async def create_feedback(payload: FeedbackIn, project_id: uuid.UUID | None = None, generation_id: uuid.UUID | None = None, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if project_id:
        await get_owned_project(db, user, project_id)
    feedback = Feedback(project_id=project_id, generation_id=generation_id, user_id=user.id, reaction=payload.reaction, categories=payload.categories, comment=payload.comment)
    db.add(feedback)
    await record_event(db, "feedback_submitted", user_id=user.id, project_id=project_id, reaction=payload.reaction)
    return {"received": True}


@router.post("/analytics/events")
async def analytics(payload: AnalyticsIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await record_event(db, payload.event_name[:128], user_id=user.id, project_id=payload.project_id, platform=payload.platform, **payload.properties)
    return {"received": True}


@router.get("/admin/metrics/summary")
async def admin_summary(_: User = Depends(admin_user), db: AsyncSession = Depends(get_db)):
    users = await db.scalar(select(func.count()).select_from(User))
    projects = await db.scalar(select(func.count()).select_from(Project))
    generations = await db.scalar(select(func.count()).select_from(Generation))
    payments = await db.scalar(select(func.count()).select_from(Payment))
    return {"users": users, "projects": projects, "generations": generations, "payments": payments}


@router.get("/admin/users", response_model=list[UserResponse])
async def admin_users(_: User = Depends(admin_user), db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(select(User).order_by(User.created_at.desc()))
    return list(rows)


@router.get("/admin/projects", response_model=list[ProjectResponse])
async def admin_projects(_: User = Depends(admin_user), db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(select(Project).order_by(Project.created_at.desc()))
    return list(rows)


@router.get("/admin/templates", response_model=list[TemplateResponse])
async def admin_templates(_: User = Depends(admin_user), db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(select(Template).order_by(Template.created_at.desc()))
    return list(rows)


@router.post("/admin/templates", response_model=TemplateResponse, status_code=201)
async def admin_create_template(payload: TemplateCreate, _: User = Depends(admin_user), db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(Template).where(Template.code == payload.code))
    if existing:
        raise HTTPException(409, "Template code already exists")
    template = Template(**payload.model_dump())
    db.add(template)
    await db.flush()
    db.add(TemplateVersion(template_id=template.id, version=1, status="active", personalization_config={"supports_inside_joke": True, "required_assets": ["sender_photo"]}))
    return template


@router.post("/admin/template-versions/{version_id}/publish")
async def admin_publish_template_version(version_id: uuid.UUID, _: User = Depends(admin_user), db: AsyncSession = Depends(get_db)):
    version = await db.get(TemplateVersion, version_id)
    if not version:
        raise HTTPException(404, "Template version not found")
    version.status = "active"
    template = await db.get(Template, version.template_id)
    if template:
        template.status = "active"
    return {"status": "published"}


async def seed_templates(db: AsyncSession):
    if await db.scalar(select(Template).limit(1)):
        return
    seeds = [
        ("secret_operation_birthday", "Секретная операция", "Брутальное поздравление с внутренней шуткой", "cinematic", ["birthday"], ["friend", "colleague", "classmate"], ["funny", "brutal"]),
        ("space_captain_anniversary", "Космический капитан", "Тёплая годовщина с капитаном корабля", "cinematic", ["anniversary", "love"], ["spouse", "partner", "parent"], ["warm", "epic", "romantic"]),
        ("warm_family_story", "Семейная история", "Трогательное семейное поздравление", "family", ["birthday", "thanks"], ["parent", "relative", "spouse"], ["warm", "touching"]),
        ("office_inside_joke", "Офисная легенда", "Поздравление коллеге с приколом", "humor", ["birthday", "professional"], ["colleague", "boss", "employee"], ["funny", "ironic"]),
        ("cinematic_universal_hero", "Главный герой", "Универсальное кино-поздравление", "cinematic", ["birthday", "anniversary", "thanks", "other"], ["friend", "colleague", "parent", "spouse", "relative", "other"], ["epic", "festive", "surprising"]),
    ]
    for code, title, desc, category, occasions, relationships, moods in seeds:
        template = Template(code=code, title=title, description=desc, category=category, occasion_codes=occasions, relationship_types=relationships, moods=moods, base_price_rub=Decimal("590"))
        db.add(template)
        await db.flush()
        db.add(TemplateVersion(template_id=template.id, version=1, prompt_config={"scenes": ["intro", "personal_joke", "greeting", "final"]}, personalization_config={"supports_inside_joke": True, "required_assets": ["sender_photo"]}))
    await db.flush()


async def generate_recommendations_for_project(db: AsyncSession, project: Project, brief: CreativeBrief):
    await seed_templates(db)
    await db.execute(Recommendation.__table__.delete().where(Recommendation.project_id == project.id))
    recipient = await db.get(Recipient, project.recipient_id)
    versions = await db.scalars(select(TemplateVersion).where(TemplateVersion.status == "active"))
    scored = []
    for version in versions:
        template = await db.get(Template, version.template_id)
        score = Decimal("0")
        reasons = []
        if project.occasion_code in template.occasion_codes or "other" in template.occasion_codes:
            score += Decimal("0.20"); reasons.append("подходит под повод")
        if recipient and (recipient.relationship in template.relationship_types or "other" in template.relationship_types):
            score += Decimal("0.20"); reasons.append("подходит под отношения")
        if brief.desired_mood and brief.desired_mood in template.moods:
            score += Decimal("0.15"); reasons.append("попадает в настроение")
        if brief.inside_joke and version.personalization_config.get("supports_inside_joke"):
            score += Decimal("0.15"); reasons.append("можно использовать личную шутку")
        if recipient and recipient.interests and template.category in " ".join(recipient.interests).lower():
            score += Decimal("0.10"); reasons.append("учитывает интересы")
        score += Decimal("0.10")
        scored.append((score, template.title, version, reasons or ["универсальный сценарий"]))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    for rank, (score, title, version, reasons) in enumerate(scored[:5], start=1):
        db.add(Recommendation(project_id=project.id, template_version_id=version.id, rank=rank, score=score, match_reasons=reasons, explanation=f"{title}: подходит для этого поздравления."))
    await record_event(db, "recommendations_generated", user_id=project.owner_user_id, project_id=project.id)


async def has_entitlement(db: AsyncSession, user_id: uuid.UUID, code: str) -> bool:
    row = await db.scalar(select(Entitlement).where(Entitlement.user_id == user_id, Entitlement.code == code, Entitlement.consumed < Entitlement.quantity))
    return row is not None


async def consume_entitlement(db: AsyncSession, user_id: uuid.UUID, code: str, project_id: uuid.UUID):
    row = await db.scalar(select(Entitlement).where(Entitlement.user_id == user_id, Entitlement.code == code, Entitlement.consumed < Entitlement.quantity))
    if not row:
        raise HTTPException(402, "Payment required")
    row.consumed += 1
    wallet = await db.scalar(select(Wallet).where(Wallet.user_id == user_id))
    db.add(WalletTransaction(wallet_id=wallet.id, type="entitlement_debit", amount_rub=Decimal("0"), project_id=project_id, description=code))


async def validate_project_ready(db: AsyncSession, user: User, project: Project):
    brief = await db.scalar(select(CreativeBrief).where(CreativeBrief.project_id == project.id))
    if not brief or brief.status != "completed":
        raise HTTPException(409, "Brief is not completed")
    if not project.selected_template_version_id:
        raise HTTPException(409, "Template is not selected")
    asset = await db.scalar(select(ProjectAsset).where(ProjectAsset.project_id == project.id, ProjectAsset.role == "sender_photo"))
    if not asset:
        raise HTTPException(409, "sender_photo asset is required")
    if project.paid_rub <= 0 and not await has_entitlement(db, user.id, "first_generation"):
        paid = await db.scalar(select(Payment).where(Payment.project_id == project.id, Payment.status == "paid"))
        if not paid:
            raise HTTPException(402, "Payment required")


async def run_mock_generation(db: AsyncSession, generation: Generation, project: Project):
    generation.status = "processing"
    generation.started_at = datetime.now(timezone.utc)
    steps = [(1, "compile_prompt", "script"), (2, "mock_video", "video"), (3, "quality_check", "final")]
    for no, code, kind in steps:
        generation.current_step = code
        generation.progress = min(95, no * 30)
        step = GenerationStep(generation_id=generation.id, step_no=no, step_code=code, type=kind, status="completed", input_json={"project_id": str(project.id)}, output_json={"mock": True}, completed_at=datetime.now(timezone.utc))
        db.add(step)
    provider = ai_router.get_video_provider()
    result = await provider.generate_video(prompt=f"Mock DarAgent video for {project.title or project.occasion_code}", duration=10)
    storage = StorageObject(bucket="daragent", object_key=f"generations/{generation.id}/result.mp4", mime_type="video/mp4", size_bytes=1024, metadata_json=result)
    db.add(storage)
    await db.flush()
    asset = Asset(owner_user_id=project.owner_user_id, type="video", status="ready", storage_object_id=storage.id, title="result.mp4", mime_type="video/mp4", duration_sec=Decimal("10"), url=result["video_url"])
    db.add(asset)
    await db.flush()
    db.add(GenerationOutput(generation_id=generation.id, asset_id=asset.id, role="final_video"))
    generation.status = "completed"
    generation.progress = 100
    generation.current_step = None
    generation.completed_at = datetime.now(timezone.utc)
    project.status = "ready"
    await record_event(db, "generation_completed", user_id=project.owner_user_id, project_id=project.id)


async def generation_assets(db: AsyncSession, generation_id: uuid.UUID) -> list[Asset]:
    rows = await db.scalars(select(Asset).join(GenerationOutput, GenerationOutput.asset_id == Asset.id).where(GenerationOutput.generation_id == generation_id))
    return list(rows)
