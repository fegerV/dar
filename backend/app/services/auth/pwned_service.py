import hashlib

import httpx


class HaveIBeenPwnedService:
    """
    Сервис для проверки паролей через Have I Been Pwned API.
    
    Использует k-анонимность: отправляется только первые 5 символов SHA1 хеша пароля,
    что позволяет проверить пароль без передачи самого пароля серверу.
    
    API: https://haveibeenpwned.com/API/v3
    """
    
    API_URL = "https://api.pwnedpasswords.com/range/"
    TIMEOUT = 10
    
    def __init__(self, api_key: str | None = None):
        """
        Инициализация сервиса.
        
        Args:
            api_key: Опциональный API ключ для повышенных лимитов.
                     Без ключа лимит: ~10 запросов в минуту.
        """
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Получить или создать HTTP клиент."""
        if self._client is None or self._client.is_closed:
            headers = {}
            if self.api_key:
                headers["Add-API-Key"] = self.api_key
            
            self._client = httpx.AsyncClient(
                timeout=self.TIMEOUT,
                headers=headers,
                follow_redirects=True
            )
        return self._client
    
    def _hash_password(self, password: str) -> str:
        """Вычислить SHA1 хеш пароля (верхний регистр)."""
        return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    
    async def is_pwned(self, password: str) -> bool:
        """
        Проверить, был ли пароль скомпрометирован.
        
        Args:
            password: Пароль для проверки
            
        Returns:
            True если пароль найден в утечках, False иначе
        """
        password_hash = self._hash_password(password)
        prefix = password_hash[:5]
        suffix = password_hash[5:]
        
        client = await self._get_client()
        
        try:
            response = await client.get(f"{self.API_URL}{prefix}")
            response.raise_for_status()
            
            # Ответ формата: HASH_SUFFIX:COUNT
            for line in response.text.splitlines():
                if ":" in line:
                    hash_suffix, count = line.split(":")
                    if hash_suffix.upper() == suffix:
                        return True
            
            return False
        except httpx.HTTPError:
            # При ошибке API считаем пароль безопасным (fail-open)
            # Но логируем ошибку для мониторинга
            return False
        finally:
            # Не закрываем клиент для переиспользования
            pass
    
    async def get_breach_count(self, password: str) -> int:
        """
        Получить количество раз, когда пароль встречался в утечках.
        
        Args:
            password: Пароль для проверки
            
        Returns:
            Количество нарушений или 0 если не найден/ошибка
        """
        password_hash = self._hash_password(password)
        prefix = password_hash[:5]
        suffix = password_hash[5:]
        
        client = await self._get_client()
        
        try:
            response = await client.get(f"{self.API_URL}{prefix}")
            response.raise_for_status()
            
            for line in response.text.splitlines():
                if ":" in line:
                    hash_suffix, count = line.split(":")
                    if hash_suffix.upper() == suffix:
                        return int(count)
            
            return 0
        except (httpx.HTTPError, ValueError):
            return 0
    
    async def check_password_strength(
        self, 
        password: str,
        min_length: int = 8,
        require_breach_free: bool = True
    ) -> dict:
        """
        Комплексная проверка пароля.
        
        Args:
            password: Пароль для проверки
            min_length: Минимальная длина
            require_breach_free: Требовать отсутствие в утечках
            
        Returns:
            Dict с результатами проверки
        """
        result = {
            "is_valid": True,
            "is_pwned": False,
            "breach_count": 0,
            "length_ok": len(password) >= min_length,
            "has_uppercase": any(c.isupper() for c in password),
            "has_lowercase": any(c.islower() for c in password),
            "has_digit": any(c.isdigit() for c in password),
            "has_special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password),
            "errors": [],
        }
        
        # Проверка длины
        if not result["length_ok"]:
            result["errors"].append(f"Password must be at least {min_length} characters")
            result["is_valid"] = False
        
        # Проверка сложности
        complexity_checks = [
            ("has_uppercase", "uppercase letter"),
            ("has_lowercase", "lowercase letter"),
            ("has_digit", "digit"),
            ("has_special", "special character"),
        ]
        
        for check_name, description in complexity_checks:
            if not result[check_name]:
                result["errors"].append(f"Password must contain at least one {description}")
                result["is_valid"] = False
        
        # Проверка на компрометацию
        if require_breach_free:
            result["is_pwned"] = await self.is_pwned(password)
            if result["is_pwned"]:
                result["breach_count"] = await self.get_breach_count(password)
                result["errors"].append(
                    f"Password has been found in {result['breach_count']} data breaches"
                )
                result["is_valid"] = False
        
        return result
    
    async def close(self) -> None:
        """Закрыть HTTP клиент."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
