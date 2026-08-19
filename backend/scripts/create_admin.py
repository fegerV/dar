"""CLI script to create the first admin user.

Usage:
    python -m scripts.create_admin admin@example.com "SecurePassword123!"
    python scripts/create_admin.py admin@example.com "SecurePassword123!" --first-name Admin --last-name User

This script must be run as a one-time bootstrap before the admin panel can be used.
It creates a User with is_admin=True and a corresponding AdminUser record.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import uuid

from sqlalchemy import func, select

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.admin import AdminUser
from app.models.user import User
from app.repositories.users import UserRepository


async def create_admin(
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
    display_name: str | None = None,
) -> dict:
    async with async_session_factory() as db:
        existing = await db.execute(select(User).where(User.email == email))
        user = existing.scalar_one_or_none()

        if user and user.is_admin:
            return {
                "status": "exists",
                "message": f"Admin user '{email}' already exists",
                "user_id": str(user.id),
            }

        if user:
            user.is_admin = True
            user.display_name = display_name or user.display_name
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            await db.flush()
        else:
            user = User(
                email=email,
                display_name=display_name or email,
                first_name=first_name,
                last_name=last_name,
                status="active",
                is_admin=True,
            )
            db.add(user)
            await db.flush()

            from app.models.user import UserAuthIdentity
            identity = UserAuthIdentity(
                user_id=user.id,
                provider="email",
                provider_user_id=email,
                email=email,
                credentials_json={"password_hash": hash_password(password)},
            )
            db.add(identity)
            await db.flush()

        admin_count = await db.execute(select(func.count()).select_from(AdminUser))
        count = admin_count.scalar() or 0

        admin_user = AdminUser(
            user_id=user.id,
            role="admin",
            is_active=True,
        )
        if count > 0:
            print(f"WARNING: {count} AdminUser records already exist. This may create inconsistency.", file=sys.stderr)
        db.add(admin_user)
        await db.commit()

        return {
            "status": "created",
            "message": f"Admin user '{email}' created successfully",
            "user_id": str(user.id),
            "admin_id": str(admin_user.id),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the first admin user")
    parser.add_argument("email", help="Admin email address")
    parser.add_argument("password", help="Password (min 8 chars, must include upper/lower/digit/special)")
    parser.add_argument("--first-name", default=None, help="First name")
    parser.add_argument("--last-name", default=None, help="Last name")
    parser.add_argument("--display-name", default=None, help="Display name")
    args = parser.parse_args()

    if len(args.password) < 8:
        print("ERROR: Password must be at least 8 characters", file=sys.stderr)
        return 1
    if not any(c.isupper() for c in args.password):
        print("ERROR: Password must contain at least one uppercase letter", file=sys.stderr)
        return 1
    if not any(c.islower() for c in args.password):
        print("ERROR: Password must contain at least one lowercase letter", file=sys.stderr)
        return 1
    if not any(c.isdigit() for c in args.password):
        print("ERROR: Password must contain at least one digit", file=sys.stderr)
        return 1

    result = asyncio.run(
        create_admin(
            email=args.email,
            password=args.password,
            first_name=args.first_name,
            last_name=args.last_name,
            display_name=args.display_name,
        )
    )

    print(f"[OK] {result['status']}: {result['message']}")
    print(f"  User ID: {result['user_id']}")
    if "admin_id" in result:
        print(f"  Admin ID: {result['admin_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
