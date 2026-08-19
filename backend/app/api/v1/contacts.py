from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.recipient import Recipient
from app.repositories.recipients import RecipientRepository

router = APIRouter(prefix="/contacts", tags=["Contacts"])

MAX_CONTACTS = 500
MAX_NAME_LENGTH = 255
MAX_NOTES_LENGTH = 1000


class ContactImportRequest(BaseModel):
    contacts: list[dict]
    consent_given: bool = False

    @field_validator("contacts")
    @classmethod
    def check_contacts_limit(cls, v):
        if len(v) > MAX_CONTACTS:
            raise ValueError(f"Too many contacts (max {MAX_CONTACTS})")
        return v


class ContactImportResponse(BaseModel):
    imported: int
    skipped: int


@router.post("/import", response_model=ContactImportResponse)
async def import_contacts(
    body: ContactImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not body.consent_given:
        from app.core.exceptions import ValidationException
        raise ValidationException(
            "Explicit consent (consent_given=true) is required for contact import. "
            "Contacts are processed locally and never sent to third-party services."
        )

    repo = RecipientRepository(db)
    imported = 0
    skipped = 0
    for contact in body.contacts:
        name = contact.get("name")
        if not name or not isinstance(name, str):
            skipped += 1
            continue
        if len(name) > MAX_NAME_LENGTH:
            name = name[:MAX_NAME_LENGTH]

        birthday_raw = contact.get("birthday")
        birth_date = None
        if birthday_raw:
            if isinstance(birthday_raw, str):
                try:
                    birth_date = datetime.fromisoformat(birthday_raw.replace("Z", "+00:00")).date()
                except (ValueError, TypeError):
                    pass
            elif isinstance(birthday_raw, datetime):
                birth_date = birthday_raw.date()

        relationship = contact.get("relationship")
        if relationship and not isinstance(relationship, str):
            relationship = str(relationship)[:MAX_NAME_LENGTH]

        notes = "Imported from contacts"
        recipient = Recipient(
            owner_user_id=current_user.id,
            first_name=name.split(" ")[0][:MAX_NAME_LENGTH],
            last_name=" ".join(name.split(" ")[1:])[:MAX_NAME_LENGTH] if " " in name else None,
            birth_date=birth_date,
            relationship=relationship,
            contact_phone=None,
            contact_email=None,
            notes=notes[:MAX_NOTES_LENGTH],
        )
        await repo.create(recipient)
        imported += 1
    await db.commit()
    return ContactImportResponse(imported=imported, skipped=skipped)
