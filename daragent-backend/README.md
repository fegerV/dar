# Дарагент MVP - Technical Baseline

## 📋 Описание

**Дарагент** — сервис для создания персонализированных AI-поздравлений.

Этот репозиторий содержит backend на FastAPI для MVP версии продукта.

## 🏗️ Архитектура

```
┌─────────────────┐     ┌─────────────────┐
│  Android App    │────▶│   Nginx         │
│  Kotlin/Compose │     │  Reverse Proxy  │
└─────────────────┘     └────────┬────────┘
                                 │
                          ┌──────▼────────┐
                          │  FastAPI API  │
                          └──────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
       ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
       │ PostgreSQL  │   │    Redis    │   │    MinIO    │
       │  Database   │   │  Cache/Queue│   │   Storage   │
       └─────────────┘   └──────┬──────┘   └─────────────┘
                                │
                         ┌──────▼──────┐
                         │   Celery    │
                         │   Workers   │
                         └─────────────┘
```

## 🛠️ Технологический стек

### Backend
- **Python 3.12+**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.x** - async ORM
- **PostgreSQL 16** - основная база данных
- **Redis** - кэш и очередь задач
- **Celery** - фоновые задачи
- **Alembic** - миграции БД
- **MinIO** - S3-compatible хранилище

### AI Providers (абстрактный слой)
- Image Generation (Replicate, Stability, etc.)
- Video Generation
- Text-to-Speech (ElevenLabs, OpenAI)
- Music Generation
- LLM (OpenAI, Anthropic)

### Infrastructure
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - reverse proxy
- **GitHub Actions** - CI/CD

## 📁 Структура проекта

```
daragent-backend/
├── api/                    # API endpoints
├── auth/                   # Authentication & authorization
├── users/                  # User management
├── templates/              # Template management
├── recommendations/        # Recommendation engine
├── prompt_compiler/        # Prompt compilation logic
├── generation/             # Generation orchestration
├── payments/               # Payment processing (YooKassa)
├── wallet/                 # Wallet & ledger system
├── webhooks/               # Webhook handlers
├── storage/                # File storage (MinIO/S3)
├── workers/                # Celery tasks
├── admin/                  # Admin panel API
├── ai_providers/           # AI provider abstraction
│   ├── base.py            # Abstract interfaces
│   ├── mock.py            # Mock providers for testing
│   └── router.py          # Provider routing
├── models/                 # SQLAlchemy models
├── schemas/                # Pydantic schemas
├── services/               # Business logic
├── repositories/           # Data access layer
├── core/                   # Core configuration
│   ├── config.py          # Settings
│   └── database.py        # DB connection
├── utils/                  # Utilities
├── migrations/             # Alembic migrations
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker Compose config
├── Dockerfile             # Docker image
└── nginx.conf             # Nginx configuration
```

## 🚀 Быстрый старт

### Предварительные требования
- Docker & Docker Compose
- Git

### Установка и запуск

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd daragent-backend
```

2. **Настройка переменных окружения**
```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

3. **Запуск всех сервисов**
```bash
docker-compose up -d
```

Это запустит:
- PostgreSQL (порт 5432)
- Redis (порт 6379)
- MinIO (порты 9000, 9001)
- FastAPI Backend (порт 8000)
- Celery Worker
- Nginx (порты 80, 443)

4. **Проверка здоровья**
```bash
curl http://localhost/health
```

5. **Просмотр логов**
```bash
docker-compose logs -f backend
docker-compose logs -f worker
```

6. **Остановка**
```bash
docker-compose down
```

## 📊 База данных

### Основные таблицы

#### users
- Пользователи системы

#### wallet_accounts & wallet_transactions
- Ledger-система для отслеживания баланса
- Все транзакции записываются в журнал

#### creative_briefs
- Входные данные от пользователя для генерации

#### generations & generation_steps & generation_assets
- Задачи генерации и их статусы
- Шаги выполнения (image, video, tts, music, assembly)
- Сгенерированные ассеты

#### templates & template_versions
- Шаблоны поздравлений
- Версионирование шаблонов

#### orders & payments
- Заказы и платежи
- Интеграция с ЮKassa

## 🔌 API Documentation

После запуска API документация доступна по адресу:
- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

## 👷 Celery Tasks

### Генерация поздравления

```python
from workers.tasks import run_generation_pipeline

# Задача выполняет полный пайплайн:
# 1. PREPARING - подготовка промтов
# 2. IMAGE_GENERATION - генерация изображений
# 3. VIDEO_GENERATION - генерация видео
# 4. TTS_GENERATION - синтез речи
# 5. MUSIC_GENERATION - генерация музыки
# 6. ASSEMBLY - сборка финального видео
# 7. QUALITY_CHECK - проверка качества
# 8. COMPLETED - завершено

task = run_generation_pipeline.delay(generation_id=1)
```

## 💰 Платежи (ЮKassa)

Интеграция с ЮKassa включает:
- Создание платежей
- Webhook обработчики
- Привязка платежей к заказам

## 🪙 Wallet System

Баланс пользователей реализуется через ledger-паттерн:

```python
# Не храним баланс напрямую
user.balance = 500  # ❌

# Храним все транзакции
+500 welcome_bonus
-100 generation
+200 promotion
-100 generation
# ✅ Баланс вычисляется из транзакций
```

## 🔐 Безопасность

- JWT токены для аутентификации
- HTTPS через Nginx
- Переменные окружения для секретов
- Non-root пользователь в Docker

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# Покрытие
pytest --cov=.
```

## 📝 Миграции БД

```bash
# Создать миграцию
alembic revision --autogenerate -m "Description"

# Применить миграции
alembic upgrade head
```

## 🔮 Планы развития

### MVP (сейчас)
- ✅ Базовая архитектура
- ✅ Модели данных
- ✅ AI Provider abstraction
- ✅ Celery pipeline
- ⏳ API endpoints
- ⏳ Auth
- ⏳ Payments integration
- ⏳ Admin panel

### Post-MVP
- Recommendation Service
- Advanced analytics
- Multiple AI providers
- A/B testing
- Monitoring (Prometheus/Grafana)

## 📄 Лицензия

[Указать лицензию]

## 👥 Команда

[Информация о команде]
