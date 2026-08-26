"""Tests for contact import service."""

import pytest

from app.services.contacts.import_service import (
    parse_contact,
    parse_csv,
    parse_date,
    parse_import_file,
    parse_json,
    parse_list_field,
    process_import,
)


class TestParseDate:
    def test_iso_format(self):
        result = parse_date("1990-05-15")
        assert result is not None
        assert result.year == 1990
        assert result.month == 5
        assert result.day == 15

    def test_european_format(self):
        result = parse_date("15.05.1990")
        assert result is not None
        assert result.year == 1990

    def test_datetime_with_timezone(self):
        result = parse_date("1990-05-15T00:00:00Z")
        assert result is not None

    def test_empty_string(self):
        assert parse_date("") is None

    def test_none(self):
        assert parse_date(None) is None

    def test_invalid(self):
        assert parse_date("not-a-date") is None


class TestParseListField:
    def test_comma_separated(self):
        result = parse_list_field("reading, gaming, music")
        assert result == ["reading", "gaming", "music"]

    def test_json_array(self):
        result = parse_list_field('["reading", "gaming"]')
        assert result == ["reading", "gaming"]

    def test_list_input(self):
        result = parse_list_field(["a", "b", "c"])
        assert result == ["a", "b", "c"]

    def test_empty(self):
        assert parse_list_field("") == []

    def test_none(self):
        assert parse_list_field(None) == []


class TestParseContact:
    def test_full_name_only(self):
        result = parse_contact({"name": "John Doe"})
        assert result is not None
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"

    def test_first_last_name(self):
        result = parse_contact({"first_name": "Jane", "last_name": "Smith"})
        assert result is not None
        assert result["first_name"] == "Jane"
        assert result["last_name"] == "Smith"

    def test_missing_name(self):
        result = parse_contact({"city": "Moscow"})
        assert result is None

    def test_gender_male(self):
        result = parse_contact({"name": "John", "gender": "male"})
        assert result["gender"] == "male"

    def test_gender_russian(self):
        result = parse_contact({"name": "Иван", "gender": "муж"})
        assert result["gender"] == "male"

    def test_birthday(self):
        result = parse_contact({"name": "John", "birthday": "1990-01-15"})
        assert result["birth_date"].year == 1990

    def test_interests(self):
        result = parse_contact({"name": "John", "interests": "reading, music"})
        assert result["interests"] == ["reading", "music"]

    def test_all_fields(self):
        result = parse_contact({
            "first_name": "Alice",
            "last_name": "Wonder",
            "nickname": "Ali",
            "gender": "female",
            "birthday": "1985-03-20",
            "city": "London",
            "occupation": "Engineer",
            "relationship": "friend",
            "phone": "+79001234567",
            "email": "alice@example.com",
            "notes": "Met at conference",
            "interests": "AI, ML",
            "traits": "creative, smart",
            "favorites": "coffee",
            "forbidden": "politics",
        })
        assert result["first_name"] == "Alice"
        assert result["last_name"] == "Wonder"
        assert result["nickname"] == "Ali"
        assert result["gender"] == "female"
        assert result["city"] == "London"
        assert result["occupation"] == "Engineer"
        assert result["relationship"] == "friend"
        assert result["contact_phone"] == "+79001234567"
        assert result["contact_email"] == "alice@example.com"
        assert result["notes"] == "Met at conference"
        assert result["interests"] == ["AI", "ML"]
        assert result["traits"] == ["creative", "smart"]
        assert result["favorite_things"] == ["coffee"]
        assert result["forbidden_topics"] == ["politics"]


class TestParseCsv:
    def test_simple_csv(self):
        csv_content = "name,birthday,city\nJohn Doe,1990-01-01,Moscow\nJane Smith,1985-05-15,SPb"
        result = parse_csv(csv_content)
        assert len(result) == 2
        assert result[0]["name"] == "John Doe"
        assert result[1]["city"] == "SPb"

    def test_csv_with_spaces(self):
        csv_content = "first_name,last_name\n  John  ,  Doe  "
        result = parse_csv(csv_content)
        assert result[0]["first_name"] == "John"


class TestParseJson:
    def test_array(self):
        json_content = '[{"name": "John"}, {"name": "Jane"}]'
        result = parse_json(json_content)
        assert len(result) == 2

    def test_object_with_contacts(self):
        json_content = '{"contacts": [{"name": "John"}]}'
        result = parse_json(json_content)
        assert len(result) == 1

    def test_single_object(self):
        json_content = '{"name": "John"}'
        result = parse_json(json_content)
        assert len(result) == 1


class TestParseImportFile:
    def test_csv_file(self):
        result = parse_import_file("contacts.csv", "name\nJohn")
        assert len(result) == 1

    def test_json_file(self):
        result = parse_import_file("contacts.json", '[{"name": "John"}]')
        assert len(result) == 1

    def test_unsupported_format(self):
        with pytest.raises(Exception):
            parse_import_file("contacts.xml", "<contacts></contacts>")


class TestProcessImport:
    def test_successful_import(self):
        contacts = [
            {"name": "John Doe"},
            {"name": "Jane Smith"},
        ]
        result = process_import(contacts)
        assert result.imported == 2
        assert result.skipped == 0

    def test_skip_invalid(self):
        contacts = [
            {"name": "John Doe"},
            {"city": "Moscow"},
        ]
        result = process_import(contacts)
        assert result.imported == 1
        assert result.skipped == 1

    def test_max_limit(self):
        contacts = [{"name": f"Person {i}"} for i in range(501)]
        with pytest.raises(Exception):
            process_import(contacts)
