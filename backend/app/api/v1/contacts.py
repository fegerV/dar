from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.recipient import Recipient
from app.repositories.recipients import RecipientRepository
from app.services.contacts.import_service import (
    ContactImportResult,
    process_import,
)

router = APIRouter(prefix="/contacts", tags=["Contacts"])


class ContactImportResponse(BaseModel):
    imported: int
    skipped: int
    errors: list[dict] = []


@router.post("/import", response_model=ContactImportResponse)
async def import_contacts(
    file: UploadFile = File(None),
    contacts: str = Form(None),
    consent_given: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not consent_given:
        from app.core.exceptions import ValidationException

        raise ValidationException(
            "Explicit consent (consent_given=true) is required for contact import. "
            "Contacts are processed locally and never sent to third-party services."
        )

    contacts_raw: list[dict] = []

    if file:
        content = await file.read()
        text = content.decode("utf-8-sig")
        from app.services.contacts.import_service import parse_import_file

        contacts_raw = parse_import_file(file.filename or "contacts.csv", text)
    elif contacts:
        import json

        contacts_raw = json.loads(contacts)
        if isinstance(contacts_raw, dict):
            contacts_raw = contacts_raw.get("contacts", [])
    else:
        from app.core.exceptions import ValidationException

        raise ValidationException("Provide a file (CSV/JSON) or contacts JSON string")

    result: ContactImportResult = process_import(contacts_raw)

    repo = RecipientRepository(db)
    for contact_data in result.contacts:
        birth_date = contact_data.get("birthday") or contact_data.get("birth_date")
        recipient = Recipient(
            owner_user_id=current_user.id,
            first_name=contact_data["first_name"],
            last_name=contact_data.get("last_name"),
            nickname=contact_data.get("nickname"),
            gender=contact_data.get("gender"),
            birth_date=birth_date,
            city=contact_data.get("city"),
            occupation=contact_data.get("occupation"),
            relationship=contact_data.get("relationship"),
            contact_phone=contact_data.get("contact_phone"),
            contact_email=contact_data.get("contact_email"),
            notes=contact_data.get("notes"),
            interests=contact_data.get("interests", []),
            traits=contact_data.get("traits", []),
            favorite_things=contact_data.get("favorite_things", []),
            forbidden_topics=contact_data.get("forbidden_topics", []),
        )
        await repo.create(recipient)

    await db.commit()

    return ContactImportResponse(
        imported=result.imported,
        skipped=result.skipped,
        errors=result.errors,
    )
