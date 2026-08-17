# 🗺️ DarAgent — Product & Tech Roadmap

> AI-сервис персональных видеопоздравлений  
> Last updated: 2026-08-17

---

## Обзор

DarAgent — платформа, которая позволяет пользователям создавать персонализированные видеопоздравления с помощью AI. Сервис автоматизирует полный цикл: от сбора информации о получателе и генерации сценария до рендеринга видео и доставки получателю.

**Текущий статус:** Фаза 1 выполнена. Переход к Фазе 2 и Фазе 3.

---

## Фаза 0: Фундамент и Инфраструктура ✅

*Цель: Подготовить среду, где можно безопасно разрабатывать и тестировать.*

| Задача | Статус | Детали |
| :--- | :--- | :--- |
| Docker Compose + Nginx | ✅ | Postgres, Redis, MinIO, Backend, Worker |
| SQLAlchemy Models (Full Schema) | ✅ | 20+ таблиц, связи, индексы, JSONB |
| Alembic Migrations | ✅ | Async engine, начальная миграция 001 |
| Auth System (JWT) | ✅ | Register, Login, Refresh, /me |
| Core Config & Exceptions | ✅ | Pydantic Settings, Unified Error Format |
| Celery Setup | ✅ | Redis broker, autodiscover |
| Seed Script | ✅ | Templates, Holidays, Relationships |
| Storage Integration (MinIO) | ✅ | Presigned URLs, upload/download |
| Payment Integration (YooKassa) | ✅ | Создание платежа, webhook, wallet, entitlements |
| Grok AI Client | ✅ | Базовая интеграция, промпт-тесты |

---

## Фаза 1: MVP Core — «От Брифа до Скрипта» (4–6 недель)

*Цель: Пользователь может создать проект, заполнить бриф и получить персонализированный текстовый сценарий.*

### 1.1 Управление Получателями (Recipients)

- [ ] CRUD API для получателей (`/api/v1/recipients`)
  - [ ] `POST /recipients` — создание
  - [ ] `GET /recipients` — список с фильтрацией и пагинацией
  - [ ] `GET /recipients/{id}` — детали
  - [ ] `PATCH /recipients/{id}` — обновление
  - [ ] `DELETE /recipients/{id}` — мягкое удаление (archive)
- [ ] Валидация данных (имя обязательно, дата рождения опциональна)
- [ ] Загрузка фото получателя (связь с Assets через `recipient_assets`)
- [ ] Поиск и фильтрация по имени, дате рождения, тегам
- [ ] Импорт контактов (CSV/JSON) — *опционально для MVP*

### 1.2 Creative Brief Wizard

- [ ] API создания/обновления брифа (`/api/v1/projects/{id}/brief`)
  - [ ] `PUT /projects/{id}/brief` — создание/обновление
  - [ ] `GET /projects/{id}/brief` — получение текущего состояния
  - [ ] `POST /projects/{id}/brief/complete` — завершение заполнения
- [ ] Пошаговая валидация (state machine: `draft → in_progress → completed`)
- [ ] Динамические вопросы на основе `relationship_type` и `occasion`
- [ ] Сохранение черновиков (autosave каждые 30 сек)
- [ ] Предпросмотр заполненного брифа перед отправкой на генерацию

### 1.3 AI Script Generation (Grok Integration)

- [ ] Доработка `GrokClient`: промпт-инжиниринг для сценариев
  - [ ] System prompt для разных типов поздравлений
  - [ ] Structured output (JSON schema enforcement)
  - [ ] Temperature tuning для креативности vs консистентности
- [ ] Сервис `ScriptGenerationService`:
  - [ ] Вход: brief + recipient + template config
  - [ ] Генерация 3 вариантов сценария
  - [ ] Парсинг ответа Grok в структурированный JSON
  - [ ] Валидация длины и содержания
- [ ] Celery task `generate_script_task`
  - [ ] Retry logic (max 3 attempts, exponential backoff)
  - [ ] Timeout handling (60s max per request)
  - [ ] Result storage в `generations.output_json`
- [ ] API получения результатов (`/api/v1/generations/{id}`)
- [ ] Механизм fallback при ошибке AI (кэшированные шаблоны)

### 1.4 Recommendations Engine (v1)

- [ ] Простой scoring algorithm:
  - [ ] Match по `occasion_code`
  - [ ] Match по `relationship_type`
  - [ ] Match по `desired_mood`
  - [ ] Weighted score → rank
- [ ] API `/api/v1/projects/{id}/recommendations`
  - [ ] `GET` — список рекомендаций с объяснениями
  - [ ] `POST /select` — выбор шаблона пользователем
- [ ] Сохранение выбора в `projects.selected_template_version_id`

### 🎯 Критерий приёмки Фазы 1

> Пользователь регистрируется → создаёт получателя → заполняет бриф → получает 3 варианта сценария → выбирает лучший.

---

## Фаза 2: Video Pipeline — «От Скрипта до Видео» (6–8 недель)

*Цель: Автоматическая генерация видео по выбранному сценарию.*

### 2.1 Asset Management System

- [x] Storage abstraction layer
  - [x] `StorageProvider` interface (MinIO, Yandex Disk, S3)
  - [x] Factory pattern для выбора провайдера по config
- [x] Upload API с presigned URLs
  - [x] `POST /assets/upload-url` — получить presigned URL
  - [x] `POST /assets/confirm-upload` — подтвердить загрузку
- [x] Проверка файлов
  - [x] MIME type validation
  - [x] Size limits (image: 10MB, video: 500MB)
  - [x] Dimensions check (min 720p for video)
- [x] Moderation queue
  - [x] Автоматическая базовая проверка (NSFW detection)
  - [x] Ручная модерация для flagged content
  - [x] Статусы: `pending → approved → rejected`
- [x] CDN-friendly URL generation
  - [x] Signed URLs с expiration
  - [x] Thumbnail generation для изображений

### 2.2 Video Generation Pipeline

- [x] Оркестратор пайплайна (Celery canvas / chain):
  ```
  script_approved
    → voice_synthesis
    → avatar_animation  
    → scene_composition
    → rendering
    → post_processing
    → upload_final
  ```
- [x] Интеграция с TTS-провайдером
  - [x] Yandex SpeechKit (primary)
  - [x] ElevenLabs (fallback/premium)
  - [ ] Voice cloning (optional, Phase 3+)
- [x] Интеграция с Video AI
  - [x] HeyGen API (primary)
  - [x] D-ID API (fallback)
  - [x] SadTalker self-hosted (cost optimization)
- [ ] Progress tracking через `generation_steps`
  - [ ] Real-time status updates
  - [ ] ETA calculation
- [ ] WebSocket/SSE endpoint для real-time прогресса в UI
  - [ ] `GET /api/v1/generations/{id}/stream`

### 2.3 Template Rendering Engine

- [ ] Парсинг `template_versions.render_config`
- [ ] Подстановка переменных в сцены (`scene_variables`)
  - [ ] Text replacement
  - [ ] Image/video insertion
  - [ ] Audio overlay
- [ ] Валидация длительности и контента
- [ ] Preview generation (low-res для быстрого просмотра)
  - [ ] 360p preview within 30 seconds
  - [ ] Watermarked

### 2.4 Quality Gate

- [ ] Автоматическая проверка:
  - [ ] Длина видео (min 15s, max 120s)
  - [ ] Разрешение (min 720p)
  - [ ] Аудио уровень (no silence, no clipping)
  - [ ] FPS consistency
- [ ] Ручная модерация финального видео
  - [ ] Admin panel для ревью
  - [ ] Approve / Reject с комментарием
- [ ] Статусы: `rendering → reviewing → approved → rejected`
- [ ] Auto-retry при технических ошибках (не при контентных)

### 🎯 Критерий приёмки Фазы 2

> Пользователь выбирает сценарий → запускает генерацию → видит прогресс → получает готовое видео → смотрит превью.

---

## Фаза 3: Монетизация и Доставка (4–5 недель)

*Цель: Превратить сервис в бизнес — оплата, доставка, шеринг.*

### 3.1 Payment System (YooKassa)

- [ ] Создание платежа
  - [ ] `POST /api/v1/payments/create`
  - [ ] Idempotency key генерация и проверка
  - [ ] Расчёт итоговой суммы (price - bonus - promo)
- [ ] Webhook обработка
  - [ ] `POST /api/v1/payments/webhook/yookassa`
  - [ ] Signature verification
  - [ ] Idempotent processing
  - [ ] Status update + entitlement grant
- [ ] Бонусная система
  - [ ] Начисление бонусов за покупки (5% cashback)
  - [ ] Списывание бонусов (max 30% от суммы)
  - [ ] История транзакций
- [ ] История платежей
  - [ ] `GET /api/v1/payments` — список
  - [ ] `GET /api/v1/payments/{id}` — детали

### 3.2 Delivery System

- [ ] Генерация защищённых ссылок
  - [ ] Cryptographically secure token
  - [ ] Expiration (default 7 days)
  - [ ] Max views limit
  - [ ] Optional password protection
- [ ] Email delivery
  - [ ] SMTP integration
  - [ ] HTML email templates
  - [ ] Tracking pixel
- [ ] Telegram Bot delivery
  - [ ] Bot API integration
  - [ ] Inline keyboard with actions
  - [ ] Video as document (no compression)
- [ ] Scheduled delivery
  - [ ] Отложенная отправка к указанной дате/времени
  - [ ] Timezone-aware scheduling
  - [ ] Cancel/reschedule

### 3.3 Sharing & Virality

- [ ] Share links с аналитикой просмотров
  - [ ] Unique link per share
  - [ ] View count tracking
  - [ ] Referral attribution
- [ ] Referral program
  - [ ] Unique referral code per user
  - [ ] Bonus for referrer + referee
  - [ ] Fraud prevention
- [ ] Social media sharing
  - [ ] Open Graph tags generation
  - [ ] Twitter Card metadata
  - [ ] Direct share buttons
- [ ] Public gallery (opt-in)
  - [ ] User consent required
  - [ ] Moderation before publish
  - [ ] Attribution to creator

### 3.4 Pricing Engine

- [ ] Расчёт цены
  - [ ] Base price from template
  - [ ] Duration multiplier
  - [ ] Personalization premium
  - [ ] HD/4K surcharge
- [ ] Промокоды
  - [ ] Fixed amount / percentage discount
  - [ ] Usage limits (per user, total)
  - [ ] Expiration date
- [ ] Пакетные предложения
  - [ ] Bundle: 3 greetings = 15% off
  - [ ] Subscription model (future)

### 🎯 Критерий приёмки Фазы 3

> Пользователь оплачивает → получает видео → отправляет получателю → получатель смотрит по ссылке.

---

## Фаза 4: UX Polish & Mobile (4–6 недель)

*Цель: Продукт, которым приятно пользоваться.*

- [ ] Responsive Web App (PWA-ready)
  - [ ] Mobile-first design
  - [ ] Service worker для offline
  - [ ] Install prompt
- [ ] Onboarding flow
  - [ ] Interactive tutorial (первый визит)
  - [ ] Demo project (попробовать без регистрации)
  - [ ] Progressive disclosure
- [ ] Dashboard
  - [ ] Мои проекты (active, completed, archived)
  - [ ] История покупок
  - [ ] Избранные получатели
  - [ ] Quick actions
- [ ] Редактор сценария
  - [ ] Post-generation text editing
  - [ ] Regenerate specific sections
  - [ ] Version history
- [ ] Push-уведомления
  - [ ] Web Push API
  - [ ] Telegram notifications
  - [ ] Email digest (weekly)
- [ ] Accessibility (a11y)
  - [ ] WCAG 2.1 AA compliance
  - [ ] Screen reader support
  - [ ] Keyboard navigation
- [ ] i18n подготовка
  - [ ] String extraction
  - [ ] EN/RU translation
  - [ ] RTL support (future)

---

## Фаза 5: Аналитика и Growth (3–4 недели)

*Цель: Data-driven развитие продукта.*

- [ ] Analytics pipeline
  - [ ] Event collection (`analytics_events` table)
  - [ ] ETL to ClickHouse / PostHog
  - [ ] Real-time dashboards
- [ ] Funnel tracking
  - [ ] Visit → Register → Create Project → Complete Brief → Pay → Deliver
  - [ ] Drop-off analysis at each step
  - [ ] Cohort retention
- [ ] A/B testing framework
  - [ ] Feature flags
  - [ ] Template variants testing
  - [ ] Pricing experiments
- [ ] Admin dashboard
  - [ ] Metabase / Grafana setup
  - [ ] Key metrics: DAU, conversion, ARPU, LTV
  - [ ] Alerting on anomalies
- [ ] Feedback collection
  - [ ] In-app NPS survey
  - [ ] CSAT after delivery
  - [ ] Feature request voting

---

## Фаза 6: Масштабирование и Безопасность (Параллельно)

### Security

- [ ] Rate limiting (per IP, per user)
- [ ] Input sanitization (XSS, SQL injection)
- [ ] Audit logs для критических действий
- [ ] GDPR compliance (data export, deletion)
- [ ] Penetration testing
- [ ] Secrets management (Vault / AWS Secrets Manager)

### Performance

- [ ] DB query optimization (EXPLAIN ANALYZE)
- [ ] Caching strategy (Redis: sessions, templates, recommendations)
- [ ] CDN for static assets and videos
- [ ] Connection pooling tuning (PgBouncer)
- [ ] Horizontal scaling (K8s / Docker Swarm)

### Reliability

- [ ] Health checks для всех сервисов
- [ ] Graceful degradation (AI down → cached templates)
- [ ] Circuit breakers для внешних API
- [ ] Backup strategy (daily DB, hourly WAL)
- [ ] Disaster recovery plan
- [ ] Chaos engineering tests

### DevOps

- [ ] CI/CD pipeline (GitHub Actions)
  - [ ] Lint + Test on PR
  - [ ] Build + Push image on merge
  - [ ] Deploy to staging automatically
  - [ ] Manual deploy to production
- [ ] Staging environment (mirror of prod)
- [ ] Monitoring stack
  - [ ] Prometheus + Grafana
  - [ ] Loki for logs
  - [ ] Alertmanager + PagerDuty
- [ ] Infrastructure as Code (Terraform / Pulumi)

### Testing

- [ ] Unit tests (>80% coverage)
  - [ ] pytest + pytest-asyncio
  - [ ] Factory boy для fixtures
- [ ] Integration tests
  - [ ] Testcontainers для Postgres/Redis
  - [ ] API contract testing
- [ ] E2E tests
  - [ ] Playwright
  - [ ] Critical user journeys
- [ ] Load testing
  - [ ] Locust scripts
  - [ ] Target: 100 RPS, p99 < 500ms

---

## 📅 Ориентировочные сроки

| Фаза | Длительность | Команда | Зависимости |
| :--- | :--- | :--- | :--- |
| Фаза 0 | ✅ Done | 1 backend | — |
| Фаза 1 | 4–6 недель | 1 backend + 1 frontend | Фаза 0 |
| Фаза 2 | 6–8 недель | 2 backend + 1 ML/AI + 1 frontend | Фаза 1 |
| Фаза 3 | 4–5 недель | 1 backend + 1 frontend | Фаза 2 |
| Фаза 4 | 4–6 недель | 1 frontend + 1 designer | Фаза 3 |
| Фаза 5 | 3–4 недели | 1 data + 1 backend | Фаза 3 |
| **Итого до Launch** | **~5–7 месяцев** | **3–5 человек** | |

---

## ⚠️ Ключевые риски и митигация

| Риск | Вероятность | Impact | Митигация |
| :--- | :--- | :--- | :--- |
| Качество AI-видео недостаточно | Высокая | Critical | Hybrid approach: AI + stock footage + human QA; A/B test провайдеров; early user testing |
| Grok API нестабилен / дорог | Средняя | High | Fallback на GPT-4o / Claude; кэширование похожих запросов; batch processing; cost monitoring |
| Низкая конверсия в оплату | Средняя | High | Freemium модель; бесплатные превью; A/B pricing; user interviews; funnel optimization |
| Права на контент / deepfake abuse | Высокая | Critical | Mandatory moderation; watermarking; ToS + content policy; age verification; takedown process |
| Долгая генерация (>5 мин) | Средняя | Medium | Queue with ETA; progressive preview; notification on complete; caching popular templates |
| Конкуренты (HeyGen, D-ID) | Высокая | Medium | Нишевая фокусировка (поздравления); superior UX; RU market first; personalization depth |
| Регуляторные изменения (AI law) | Средняя | High | Monitor legislation; flexible architecture; legal consultation; compliance buffer |

---

## 🎯 Следующие шаги (Sprint 1)

1. **Завершить Фазу 0** (1 неделя)
   - [ ] Дописать MinIO storage adapter
   - [ ] Дописать YooKassa client (stub)
   - [ ] Запустить `docker compose up`, применить миграцию
   - [ ] Написать базовые health-check тесты

2. **Начать Фазу 1.1: Recipients CRUD** (2 недели)
   - [ ] Repository + Service для Recipients
   - [ ] API endpoints + Pydantic schemas
   - [ ] Unit + integration tests
   - [ ] API documentation (OpenAPI)

3. **Параллельно: Grok Prompt Engineering** (ongoing)
   - [ ] Тестировать промпты для разных occasions
   - [ ] Оценить качество вывода (human eval)
   - [ ] Определить optimal temperature / max_tokens
   - [ ] Документировать best practices

4. **Frontend Kickoff** (1 неделя)
   - [ ] Выбрать стек (Next.js 14 App Router recommended)
   - [ ] Настроить проект + ESLint + Prettier
   - [ ] Сделать login/register страницы
   - [ ] Design system foundation (shadcn/ui)

---

## 📚 Полезные ссылки

- [Техническое задание](./ДарАГЕНТ.txt)
- [API Documentation](./docs/api.md) *(TODO)*
- [Architecture Decision Records](./docs/adr/) *(TODO)*
- [Figma Designs](https://figma.com/file/xxx) *(TODO)*
- [Notion Board](https://notion.so/xxx) *(TODO)*

---

*Этот документ является живым и обновляется по мере развития проекта. Последнее обновление: 2026-08-17.*
