"""Contact import service for CSV/JSON file parsing."""

import csv
import io
import json
import logging
from datetime import datetime
from typing import Any

from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)

MAX_CONTACTS = 500
MAX_NAME_LENGTH = 255
MAX_NOTES_LENGTH = 1000
MAX_FIELD_LENGTH = 500

CSV_COLUMN_MAPPING = {
    "name": "name",
    "first_name": "first_name",
    "firstname": "first_name",
    "last_name": "last_name",
    "lastname": "last_name",
    "nickname": "nickname",
    "gender": "gender",
    "birthday": "birthday",
    "birth_date": "birthday",
    "date_of_birth": "birthday",
    "city": "city",
    "occupation": "occupation",
    "job": "occupation",
    "relationship": "relationship",
    "relation": "relationship",
    "phone": "contact_phone",
    "contact_phone": "contact_phone",
    "telephone": "contact_phone",
    "email": "contact_email",
    "contact_email": "contact_email",
    "e-mail": "contact_email",
    "notes": "notes",
    "note": "notes",
    "interests": "interests",
    "interest": "interests",
    "hobbies": "interests",
    "traits": "traits",
    "trait": "traits",
    "characteristics": "traits",
    "favorites": "favorite_things",
    "favorite": "favorite_things",
    "favourite": "favorite_things",
    "favorite_things": "favorite_things",
    "forbidden": "forbidden_topics",
    "forbidden_topics": "forbidden_topics",
    "avoid": "forbidden_topics",
}


class ContactImportResult:
    def __init__(self):
        self.imported = 0
        self.skipped = 0
        self.errors: list[dict[str, Any]] = []
        self.contacts: list[dict[str, Any]] = []


def parse_date(value: Any) -> Any:
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None

    formats = [
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except (ValueError, TypeError):
        pass

    return None


def parse_list_field(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if v and str(v).strip()]
    if isinstance(value, str):
        if value.startswith("["):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(v).strip() for v in parsed if v and str(v).strip()]
            except json.JSONDecodeError:
                pass
        return [v.strip() for v in value.split(",") if v.strip()]
    return []


def normalize_column_name(col: str) -> str:
    return col.lower().strip().replace(" ", "_").replace("-", "_")


def map_fields(row: dict[str, Any]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for col, value in row.items():
        normalized = normalize_column_name(col)
        field_name = CSV_COLUMN_MAPPING.get(normalized)
        if field_name and value is not None and str(value).strip():
            mapped[field_name] = value
    return mapped


def parse_contact(raw: dict[str, Any]) -> dict[str, Any] | None:
    mapped = map_fields(raw)

    name = mapped.get("name", "")
    first_name = mapped.get("first_name", "")
    last_name = mapped.get("last_name", "")

    if not name and not first_name:
        return None

    if name and not first_name:
        parts = name.strip().split(None, 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

    contact: dict[str, Any] = {
        "first_name": first_name[:MAX_NAME_LENGTH],
        "last_name": (last_name or None),
    }

    if mapped.get("nickname"):
        contact["nickname"] = str(mapped["nickname"])[:MAX_NAME_LENGTH]

    if mapped.get("gender"):
        gender = str(mapped["gender"]).lower().strip()
        if gender in ("male", "m", "м", "муж", "мужской"):
            contact["gender"] = "male"
        elif gender in ("female", "f", "ж", "жен", "женский"):
            contact["gender"] = "female"
        elif gender in ("other", "o", "другое"):
            contact["gender"] = "other"

    if mapped.get("birthday"):
        birth_date = parse_date(mapped["birthday"])
        if birth_date:
            contact["birth_date"] = birth_date

    if mapped.get("city"):
        contact["city"] = str(mapped["city"])[:MAX_NAME_LENGTH]

    if mapped.get("occupation"):
        contact["occupation"] = str(mapped["occupation"])[:MAX_NAME_LENGTH]

    if mapped.get("relationship"):
        contact["relationship"] = str(mapped["relationship"])[:30]

    if mapped.get("contact_phone"):
        contact["contact_phone"] = str(mapped["contact_phone"])[:30]

    if mapped.get("contact_email"):
        contact["contact_email"] = str(mapped["contact_email"])[:255]

    if mapped.get("notes"):
        contact["notes"] = str(mapped["notes"])[:MAX_NOTES_LENGTH]

    if mapped.get("interests"):
        contact["interests"] = parse_list_field(mapped["interests"])

    if mapped.get("traits"):
        contact["traits"] = parse_list_field(mapped["traits"])

    if mapped.get("favorite_things"):
        contact["favorite_things"] = parse_list_field(mapped["favorite_things"])

    if mapped.get("forbidden_topics"):
        contact["forbidden_topics"] = parse_list_field(mapped["forbidden_topics"])

    return contact


def parse_csv(content: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    for row in reader:
        cleaned = {k.strip(): v.strip() if v else v for k, v in row.items() if k and k.strip()}
        if any(v and v.strip() for v in cleaned.values()):
            rows.append(cleaned)
    return rows


def parse_json(content: str) -> list[dict[str, Any]]:
    data = json.loads(content)
    if isinstance(data, dict):
        if "contacts" in data:
            data = data["contacts"]
        else:
            data = [data]
    if not isinstance(data, list):
        raise ValidationException("JSON must be an array of contacts or object with 'contacts' key")
    return data


def parse_import_file(filename: str, content: str) -> list[dict[str, Any]]:
    lower = filename.lower()
    if lower.endswith(".csv"):
        return parse_csv(content)
    elif lower.endswith(".json"):
        return parse_json(content)
    else:
        raise ValidationException("Unsupported file format. Use .csv or .json")


def process_import(contacts_raw: list[dict[str, Any]]) -> ContactImportResult:
    result = ContactImportResult()

    if len(contacts_raw) > MAX_CONTACTS:
        raise ValidationException(f"Too many contacts (max {MAX_CONTACTS})")

    for idx, raw in enumerate(contacts_raw):
        try:
            contact = parse_contact(raw)
            if contact is None:
                result.skipped += 1
                result.errors.append({
                    "row": idx + 1,
                    "status": "skipped",
                    "reason": "Missing name or first_name",
                })
                continue
            result.contacts.append(contact)
            result.imported += 1
        except Exception as e:
            logger.warning("Failed to parse contact at row %d: %s", idx + 1, e)
            result.skipped += 1
            result.errors.append({
                "row": idx + 1,
                "status": "error",
                "reason": str(e),
            })

    return result
