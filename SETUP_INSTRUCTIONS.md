# Инструкция по запуску бэкенда и админки

## Быстрый старт (локальная разработка)

### 1. Запуск инфраструктуры (PostgreSQL, Redis, MinIO)

```bash
docker-compose -f docker-compose.local.yml up -d
```

### 2. Настройка бэкенда

Файл `.env` для бэкенда уже создан в `/workspace/backend/.env`.

Запуск бэкенда:

```bash
cd /workspace/backend

# Установка зависимостей (если нужно)
pip install -e .

# Применение миграций
alembic upgrade head

# Запуск сервера
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Или через Docker Compose (полный стек):

```bash
docker-compose up -d postgres redis minio backend worker celery_beat
```

### 3. Создание первого администратора

#### Вариант A: Через CLI скрипт (рекомендуется)

```bash
cd /workspace/backend
python -m scripts.create_admin admin@daragent.ru "AdminPassword123!" \
    --first-name Admin \
    --last-name User \
    --display-name "Администратор"
```

#### Вариант B: Через API endpoint `/admin/setup`

Используйте bootstrap токен из `.env` (`ADMIN_BOOTSTRAP_TOKEN=dev-bootstrap-token-12345`):

```bash
curl -X POST http://localhost:8000/api/v1/admin/setup \
  -H "Content-Type: application/json" \
  -H "X-Bootstrap-Token: dev-bootstrap-token-12345" \
  -d '{
    "email": "admin@daragent.ru",
    "password": "AdminPassword123!",
    "first_name": "Admin",
    "last_name": "User",
    "display_name": "Администратор"
  }'
```

#### Вариант C: Через веб-интерфейс

1. Откройте `http://localhost:3000/admin/init`
2. Заполните форму создания администратора
3. После успешного создания вы будете перенаправлены на страницу входа

### 4. Настройка веб-приложения (админка)

Файл `.env.local` для веб-приложения уже создан в `/workspace/web-app/.env.local`.

Запуск веб-приложения:

```bash
cd /workspace/web-app

# Установка зависимостей (если нужно)
npm install

# Запуск dev-сервера
npm run dev
```

Или через Docker Compose:

```bash
docker-compose up -d web-app
```

### 5. Вход в админку

1. Откройте `http://localhost:3000/admin/login`
2. Введите email и пароль, указанные при создании администратора
3. После входа вы попадете на дашборд `http://localhost:3000/admin/dashboard`

## Полный стек через Docker Compose

Для запуска всего стека (бэкенд, фронтенд, БД, кэш, хранилище):

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## Переменные окружения

### Бэкенд (`/workspace/backend/.env`)

Ключевые переменные:
- `APP_ENV=development` - режим разработки
- `DATABASE_URL` - подключение к PostgreSQL
- `REDIS_URL` - подключение к Redis
- `JWT_SECRET_KEY` - секрет для JWT токенов
- `ADMIN_BOOTSTRAP_TOKEN` - токен для создания первого админа

### Веб-приложение (`/workspace/web-app/.env.local`)

Ключевые переменные:
- `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1` - URL бэкенда
- `NEXT_PUBLIC_ADMIN_BOOTSTRAP_TOKEN` - токен для bootstrap endpoint

## Проверка работы

### Health check бэкенда

```bash
curl http://localhost:8000/health/detailed
```

### Проверка API

```bash
# Получить статистику админки (требуется авторизация)
curl http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Адреса сервисов

| Сервис | URL |
|--------|-----|
| Backend API | http://localhost:8000 |
| Web App (Admin) | http://localhost:3000 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| MinIO Console | http://localhost:9001 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (порт может конфликтовать с web-app) |

## Troubleshooting

### Ошибка подключения к БД

Убедитесь, что PostgreSQL запущен:
```bash
docker-compose -f docker-compose.local.yml ps
```

### Миграции не применены

```bash
cd /workspace/backend
alembic upgrade head
```

### Ошибка "Admin already exists"

Первый администратор уже создан. Используйте его credentials для входа или удалите запись из БД.

### Токен доступа истек

Используйте refresh token для получения нового access token через endpoint `/auth/refresh`.
