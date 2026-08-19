from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.recipient import Recipient
from app.repositories.recipients import RecipientRepository

router = APIRouter(prefix="/contacts", tags=["Contacts"])


class ContactImportRequest(BaseModel):
    contacts: list[dict]


class ContactImportResponse(BaseModel):
    imported: int
    skipped: int


@router.post("/import", response_model=ContactImportResponse)
async def import_contacts(
    body: ContactImportRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = RecipientRepository(db)
    imported = 0
    skipped = 0
    for contact in body.contacts:
        name = contact.get("name")
        birthday = contact.get("birthday")
        if not name:
            skipped += 1
            continue
        recipient = Recipient(
            owner_user_id=current_user.id,
            first_name=name.split(" ")[0],
            last_name=" ".join(name.split(" ")[1:]) if " " in name else None,
            birth_date=birthday,
            relationship=contact.get("relationship"),
            contact_phone=None,
            contact_email=None,
            notes="Imported from contacts",
        )
        await repo.create(recipient)
        imported += 1
    await db.commit()
    return ContactImportResponse(imported=imported, skipped=skipped)
