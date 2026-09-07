import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any
from uuid import UUID

import pyotp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.security import hash_password, verify_password
from app.models.two_factor_auth import TwoFactorAuth
from app.models.user import User


class TwoFactorAuthService:
    """Сервис для управления двухфакторной аутентификацией TOTP."""
    
    ISSUER_NAME = "Daragent"
    BACKUP_CODES_COUNT = 10
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def _get_2fa_for_user(self, user_id: UUID) -> TwoFactorAuth | None:
        """Получить настройки 2FA для пользователя."""
        result = await self.db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    def generate_totp_secret(self) -> str:
        """Сгенерировать новый TOTP секрет."""
        return pyotp.random_base32()
    
    def get_provisioning_uri(self, secret: str, email: str) -> str:
        """Сгенерировать URI для provisioning в authenticator app."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=self.ISSUER_NAME)
    
    def verify_totp(self, secret: str, code: str, window: int = 1) -> bool:
        """Проверить TOTP код с учетом временного окна."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=window)
    
    def generate_backup_codes(self) -> list[str]:
        """Сгенерировать одноразовые backup коды."""
        codes = []
        for _ in range(self.BACKUP_CODES_COUNT):
            code = f"{secrets.randbelow(10**8):08d}"
            codes.append(code)
        return codes
    
    async def enable_2fa(self, user_id: UUID, totp_code: str) -> dict[str, Any]:
        """
        Включить 2FA для пользователя.
        
        Args:
            user_id: ID пользователя
            totp_code: Код из authenticator app для верификации
            
        Returns:
            Dict с backup кодами (показываются только один раз)
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedException("User not found")
        
        # Проверяем, не включен ли уже 2FA
        existing = await self._get_2fa_for_user(user_id)
        if existing and existing.is_enabled:
            raise ValidationException("2FA already enabled")
        
        # Генерируем секрет
        secret = self.generate_totp_secret()
        
        # Верифицируем код
        if not self.verify_totp(secret, totp_code):
            raise ValidationException("Invalid TOTP code")
        
        # Генерируем backup коды
        backup_codes = self.generate_backup_codes()
        hashed_codes = [hash_password(code) for code in backup_codes]
        
        # Сохраняем или обновляем запись
        if existing:
            existing.totp_secret = secret
            existing.is_enabled = True
            existing.backup_codes = json.dumps(hashed_codes)
            existing.updated_at = time.time()
        else:
            two_fa = TwoFactorAuth(
                user_id=user_id,
                totp_secret=secret,
                is_enabled=True,
                backup_codes=json.dumps(hashed_codes),
            )
            self.db.add(two_fa)
        
        await self.db.commit()
        
        # Возвращаем backup коды (только один раз!)
        return {
            "backup_codes": backup_codes,
            "message": "Save these backup codes securely. They will not be shown again."
        }
    
    async def disable_2fa(self, user_id: UUID, totp_code: str | None = None, 
                          backup_code: str | None = None) -> None:
        """
        Отключить 2FA для пользователя.
        
        Args:
            user_id: ID пользователя
            totp_code: Код из authenticator app ИЛИ
            backup_code: Backup код для верификации
        """
        two_fa = await self._get_2fa_for_user(user_id)
        if not two_fa or not two_fa.is_enabled:
            raise ValidationException("2FA not enabled")
        
        # Верификация через TOTP или backup код
        verified = False
        
        if totp_code and self.verify_totp(two_fa.totp_secret, totp_code):
            verified = True
        elif backup_code:
            hashed_codes = json.loads(two_fa.backup_codes) if two_fa.backup_codes else []
            for hashed_code in hashed_codes:
                if verify_password(backup_code, hashed_code):
                    # Удаляем использованный код
                    hashed_codes.remove(hashed_code)
                    two_fa.backup_codes = json.dumps(hashed_codes)
                    verified = True
                    break
        
        if not verified:
            raise UnauthorizedException("Invalid verification code")
        
        two_fa.is_enabled = False
        two_fa.totp_secret = ""
        two_fa.backup_codes = json.dumps([])
        two_fa.updated_at = time.time()
        
        await self.db.commit()
    
    async def verify_2fa(self, user_id: UUID, code: str) -> bool:
        """
        Проверить 2FA код при логине.
        
        Args:
            user_id: ID пользователя
            code: TOTP код или backup код
            
        Returns:
            True если верификация успешна
        """
        two_fa = await self._get_2fa_for_user(user_id)
        if not two_fa or not two_fa.is_enabled:
            # Если 2FA не включен, считаем верификацию успешной
            return True
        
        # Проверяем TOTP
        if self.verify_totp(two_fa.totp_secret, code):
            two_fa.last_used_at = time.time()
            await self.db.commit()
            return True
        
        # Проверяем backup код
        hashed_codes = json.loads(two_fa.backup_codes) if two_fa.backup_codes else []
        for hashed_code in hashed_codes:
            if verify_password(code, hashed_code):
                # Удаляем использованный код
                hashed_codes.remove(hashed_code)
                two_fa.backup_codes = json.dumps(hashed_codes)
                two_fa.last_used_at = time.time()
                await self.db.commit()
                return True
        
        return False
    
    async def regenerate_backup_codes(self, user_id: UUID, totp_code: str) -> dict[str, Any]:
        """
        Перегенерировать backup коды.
        
        Args:
            user_id: ID пользователя
            totp_code: Код из authenticator app для верификации
            
        Returns:
            Dict с новыми backup кодами
        """
        two_fa = await self._get_2fa_for_user(user_id)
        if not two_fa or not two_fa.is_enabled:
            raise ValidationException("2FA not enabled")
        
        if not self.verify_totp(two_fa.totp_secret, totp_code):
            raise UnauthorizedException("Invalid TOTP code")
        
        # Генерируем новые коды
        backup_codes = self.generate_backup_codes()
        hashed_codes = [hash_password(code) for code in backup_codes]
        
        two_fa.backup_codes = json.dumps(hashed_codes)
        two_fa.updated_at = time.time()
        
        await self.db.commit()
        
        return {
            "backup_codes": backup_codes,
            "message": "Save these backup codes securely. They will not be shown again."
        }
    
    async def get_2fa_status(self, user_id: UUID) -> dict[str, Any]:
        """Получить статус 2FA для пользователя."""
        two_fa = await self._get_2fa_for_user(user_id)
        
        if not two_fa:
            return {
                "is_enabled": False,
                "setup_required": True,
            }
        
        return {
            "is_enabled": two_fa.is_enabled,
            "setup_required": False,
            "has_backup_codes": bool(two_fa.backup_codes and json.loads(two_fa.backup_codes)),
            "last_used_at": two_fa.last_used_at,
        }
    
    async def initiate_2fa_setup(self, user_id: UUID) -> dict[str, str]:
        """
        Инициировать настройку 2FA (получить секрет и QR URI).
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict с секретом и provisioning URI
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedException("User not found")
        
        # Проверяем, не включен ли уже 2FA
        existing = await self._get_2fa_for_user(user_id)
        if existing and existing.is_enabled:
            raise ValidationException("2FA already enabled")
        
        secret = self.generate_totp_secret()
        provisioning_uri = self.get_provisioning_uri(
            secret, 
            user.email or str(user_id)
        )
        
        # Временно сохраняем секрет (но не включаем 2FA)
        if existing:
            existing.totp_secret = secret
            existing.is_enabled = False
        else:
            two_fa = TwoFactorAuth(
                user_id=user_id,
                totp_secret=secret,
                is_enabled=False,
            )
            self.db.add(two_fa)
        
        await self.db.commit()
        
        return {
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "manual_entry_key": base64.b32decode(secret).hex().upper(),
        }
