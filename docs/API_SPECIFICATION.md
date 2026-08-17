# ДарАгент MVP — API Specification v0.2

## Base URL
```
Production: https://api.daragent.ru/api/v1
Staging: https://api-staging.daragent.ru/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication
Все endpoints кроме `/auth/register`, `/auth/login` и `/health` требуют JWT токен в заголовке:
```
Authorization: Bearer <access_token>
```

## Общие коды ответов
- `200` - Успех
- `201` - Создано
- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Нет доступа
- `404` - Не найдено
- `409` - Конфликт
- `422` - Ошибка валидации данных
- `429` - Слишком много запросов
- `500` - Внутренняя ошибка сервера

---

## 1. Auth

### POST /auth/register
Регистрация нового пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "name": "Иван Петров",
  "password": "SecurePass123!",
  "auth_provider": "email",
  "auth_provider_id": "user@example.com"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /auth/login
Вход в систему.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /auth/refresh
Обновление access токена.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /auth/logout
Выход из системы (отзыв refresh токена).

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "success": true
}
```

---

## 2. Users

### GET /me
Получение профиля текущего пользователя.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "phone": null,
  "name": "Иван Петров",
  "avatar_url": "https://storage.daragent.ru/avatars/...",
  "auth_provider": "email",
  "balance": 500,
  "bonus_balance": 100,
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### PUT /me
Обновление профиля.

**Request:**
```json
{
  "name": "Иван Иванов",
  "avatar_url": "https://storage.daragent.ru/avatars/..."
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "Иван Иванов",
  ...
}
```

---

## 3. Recipients

### POST /recipients
Создание получателя поздравления.

**Request:**
```json
{
  "name": "Александр",
  "gender": "male",
  "age": 40,
  "relationship": "friend",
  "interests": ["cars", "travel", "football"],
  "personality": ["funny", "confident", "energetic"],
  "additional_info": "Любит активный отдых"
}
```

**Response (201):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Александр",
  "gender": "male",
  "age": 40,
  "relationship": "friend",
  "interests": ["cars", "travel", "football"],
  "personality": ["funny", "confident", "energetic"],
  "additional_info": "Любит активный отдых",
  "photo_asset_id": null,
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}
```

### GET /recipients
Список получателей пользователя.

**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 20, max: 100)

**Response (200):**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Александр",
      "relationship": "friend",
      ...
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

### GET /recipients/{recipient_id}
Детали получателя.

**Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Александр",
  ...
}
```

### PUT /recipients/{recipient_id}
Обновление получателя.

**Request:**
```json
{
  "age": 41,
  "interests": ["cars", "travel", "football", "cooking"]
}
```

### DELETE /recipients/{recipient_id}
Удаление получателя.

**Response (204):** No Content

---

## 4. Projects

### POST /projects
Создание нового проекта (поздравления).

**Request:**
```json
{
  "recipient_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "День рождения Александра",
  "occasion": "birthday",
  "format": "medium_30s"
}
```

**Response (201):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "recipient_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "День рождения Александра",
  "status": "draft",
  "occasion": "birthday",
  "format": "medium_30s",
  "creative_brief": null,
  "selected_template_id": null,
  "selected_template_version_id": null,
  "price": 0,
  "currency": "RUB",
  "created_at": "2025-01-15T11:30:00Z",
  "updated_at": "2025-01-15T11:30:00Z",
  "completed_at": null
}
```

### GET /projects
Список проектов пользователя.

**Query Parameters:**
- `status` (optional, filter by status)
- `page` (int, default: 1)
- `page_size` (int, default: 20, max: 100)

**Response (200):**
```json
{
  "items": [...],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

### GET /projects/{project_id}
Детали проекта.

**Response (200):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "recipient_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "День рождения Александра",
  "status": "brief_ready",
  "occasion": "birthday",
  "format": "medium_30s",
  "creative_brief": {
    "occasion": "birthday",
    "recipient": {...},
    ...
  },
  ...
}
```

### PUT /projects/{project_id}
Обновление проекта.

**Request:**
```json
{
  "title": "Юбилей Александра"
}
```

### DELETE /projects/{project_id}
Удаление проекта.

**Response (204):** No Content

---

## 5. Creative Brief

### PUT /projects/{project_id}/brief
Создание/обновление Creative Brief для проекта.

**Request:**
```json
{
  "occasion": "birthday",
  "recipient": {
    "name": "Александр",
    "age": 40,
    "gender": "male",
    "relationship": "friend"
  },
  "sender": {
    "name": "Виктор",
    "relationship": "friend"
  },
  "personality": ["funny", "confident", "energetic"],
  "interests": ["cars", "travel", "football"],
  "tone": {
    "humor": 0.8,
    "emotion": 0.6,
    "seriousness": 0.2,
    "warmth": 0.7
  },
  "style": "cinematic",
  "duration": 60,
  "surprise_level": 0.9
}
```

**Response (200):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "brief_ready",
  "creative_brief": {...},
  "updated_at": "2025-01-15T11:45:00Z"
}
```

---

## 6. Recommendations

### POST /projects/{project_id}/recommendations
Генерация рекомендаций шаблонов на основе Creative Brief.

**Response (200):**
```json
{
  "project_id": "770e8400-e29b-41d4-a716-446655440002",
  "recommendations": [
    {
      "template_id": "550e8400-e29b-41d4-a716-446655440003",
      "template_name": "Герой фильма",
      "score": 0.94,
      "reason": "Подходит для близкого друга с хорошим чувством юмора",
      "preview_url": "https://storage.daragent.ru/previews/...",
      "price": 299,
      "category": "cinematic",
      "duration_estimate": 60
    },
    {
      "template_id": "550e8400-e29b-41d4-a716-446655440004",
      "template_name": "Голливудский трейлер",
      "score": 0.88,
      "reason": "Отлично подходит для любителей кино",
      "price": 349,
      "category": "cinematic",
      "duration_estimate": 60
    }
  ],
  "generated_at": "2025-01-15T11:50:00Z"
}
```

---

## 7. Templates

### GET /templates
Список доступных шаблонов.

**Query Parameters:**
- `category` (optional)
- `occasion` (optional)
- `price_tier` (optional)
- `min_price` (optional)
- `max_price` (optional)
- `page` (int, default: 1)
- `page_size` (int, default: 20)

**Response (200):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "template_id": "movie_hero_001",
      "name": "Герой фильма",
      "description": "Поздравление в стиле голливудского блокбастера",
      "category": "cinematic",
      "price_tier": "standard",
      "base_price": 299,
      "is_published": true,
      "popularity_score": 150,
      ...
    }
  ],
  "total": 40,
  "page": 1,
  "page_size": 20
}
```

### GET /templates/{template_id}
Детали шаблона.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "template_id": "movie_hero_001",
  "name": "Герой фильма",
  "description": "Поздравление в стиле голливудского блокбастера",
  "category": "cinematic",
  "price_tier": "standard",
  "base_price": 299,
  "is_published": true,
  "versions": [
    {
      "id": "...",
      "version": 1,
      "name": "Версия 1",
      "is_active": true,
      ...
    }
  ]
}
```

### POST /projects/{project_id}/template
Выбор шаблона для проекта.

**Request:**
```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440003",
  "template_version_id": "880e8400-e29b-41d4-a716-446655440005"
}
```

**Response (200):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "template_selected",
  "selected_template_id": "550e8400-e29b-41d4-a716-446655440003",
  "selected_template_version_id": "880e8400-e29b-41d4-a716-446655440005",
  "price": 299,
  "updated_at": "2025-01-15T12:00:00Z"
}
```

---

## 8. Generations

### POST /projects/{project_id}/generate
Запуск генерации поздравления.

**Response (202):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440006",
  "project_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "queued",
  "created_at": "2025-01-15T12:05:00Z"
}
```

### GET /generations/{generation_id}
Статус генерации.

**Response (200):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440006",
  "project_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "generating_assets",
  "retry_count": 0,
  "error_code": null,
  "error_message": null,
  "script_content": null,
  "assets_json": [],
  "video_url": null,
  "preview_url": null,
  "started_at": "2025-01-15T12:05:30Z",
  "completed_at": null,
  "created_at": "2025-01-15T12:05:00Z",
  "steps": [
    {
      "id": "...",
      "step_type": "script",
      "step_order": 1,
      "status": "ready",
      ...
    },
    {
      "id": "...",
      "step_type": "image",
      "step_order": 2,
      "status": "generating_video",
      ...
    }
  ]
}
```

### POST /generations/{generation_id}/retry
Повторная попытка генерации после ошибки.

**Response (202):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440006",
  "status": "queued",
  "retry_count": 1
}
```

---

## 9. Preview

### GET /projects/{project_id}/preview
Получение превью готового поздравления.

**Response (200):**
```json
{
  "project_id": "770e8400-e29b-41d4-a716-446655440002",
  "preview_url": "https://storage.daragent.ru/previews/...",
  "video_url": null,
  "expires_at": "2025-01-15T14:05:00Z"
}
```

---

## 10. Payments

### POST /payments
Создание платежа.

**Request:**
```json
{
  "project_id": "770e8400-e29b-41d4-a716-446655440002",
  "amount": 299,
  "payment_method": "yookassa",
  "description": "Оплата поздравления \"День рождения Александра\""
}
```

**Response (201):**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440007",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "770e8400-e29b-41d4-a716-446655440002",
  "amount": 299,
  "currency": "RUB",
  "status": "pending",
  "payment_method": "yookassa",
  "provider_payment_id": "2d3df78f-000e-500b-9000-jk8441zxjzPP",
  "confirmation_url": "https://yookassa.ru/checkout/...",
  "created_at": "2025-01-15T12:10:00Z"
}
```

### GET /payments/{payment_id}
Статус платежа.

**Response (200):**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440007",
  "amount": 299,
  "status": "succeeded",
  "paid_at": "2025-01-15T12:12:00Z",
  ...
}
```

### POST /payments/webhook
Webhook от ЮKassa (внутренний endpoint).

**Request:**
```json
{
  "type": "notification",
  "event": "payment.succeeded",
  "object": {
    "id": "2d3df78f-000e-500b-9000-jk8441zxjzPP",
    "status": "succeeded",
    "amount": {
      "value": "299.00",
      "currency": "RUB"
    },
    "metadata": {
      "project_id": "770e8400-e29b-41d4-a716-446655440002",
      "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

**Response (200):**
```json
{
  "success": true
}
```

---

## 11. Wallet

### GET /wallet
Баланс пользователя.

**Response (200):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "balance": 500,
  "bonus_balance": 100,
  "currency": "RUB",
  "updated_at": "2025-01-15T12:12:00Z"
}
```

### GET /wallet/transactions
История транзакций.

**Query Parameters:**
- `transaction_type` (optional)
- `page` (int, default: 1)
- `page_size` (int, default: 50)

**Response (200):**
```json
{
  "items": [
    {
      "id": "...",
      "transaction_type": "deposit",
      "amount": 500,
      "balance_after": 500,
      "description": "Пополнение баланса",
      "created_at": "2025-01-15T10:00:00Z"
    },
    {
      "id": "...",
      "transaction_type": "generation",
      "amount": -299,
      "balance_after": 201,
      "related_entity_type": "project",
      "related_entity_id": "770e8400-e29b-41d4-a716-446655440002",
      "description": "Генерация поздравления",
      "created_at": "2025-01-15T12:12:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 50
}
```

---

## 12. Bonuses

### GET /bonuses
Активные бонусы пользователя.

**Response (200):**
```json
{
  "items": [
    {
      "id": "...",
      "bonus_type": "registration",
      "amount": 100,
      "remaining_amount": 100,
      "expires_at": "2025-02-15T00:00:00Z",
      "is_active": true,
      "granted_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

## 13. Analytics

### POST /analytics/events
Отправка аналитического события.

**Request:**
```json
{
  "event_name": "template_selected",
  "project_id": "770e8400-e29b-41d4-a716-446655440002",
  "properties": {
    "template_id": "movie_hero_001"
  },
  "session_id": "sess_abc123"
}
```

**Response (201):**
```json
{
  "id": "...",
  "event_name": "template_selected",
  "created_at": "2025-01-15T12:00:00Z"
}
```

---

## 14. Health & Status

### GET /health
Проверка здоровья сервиса.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T12:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "storage": "connected"
  }
}
```

---

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| /auth/* | 10 req/min |
| /projects | 100 req/min |
| /generations | 20 req/min |
| /payments | 30 req/min |
| /analytics/events | 100 req/min |
| Остальные | 60 req/min |

Headers для rate limiting:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705320000
```
