# 🗺️ DarAgent — Product & Tech Roadmap

> AI-сервис персональных видеопоздравлений  
> Last updated: 2026-08-17

---

## Обзор

DarAgent — платформа, которая позволяет пользователям создавать персонализированные видеопоздравления с помощью AI. Сервис автоматизирует полный цикл: от сбора информации о получателе и генерации сценария до рендеринга видео и доставки получателю.

**Текущий статус:** Фаза 0–1, 2.1–2.2, 3.1–3.3 и 5 выполнены. Переход к Фазе 6 и оставшимся пунктам 2.3/3.2.

**Ключевой принцип MVP:** Пользователь не создаёт контент с нуля. Он выбирает повод → человека → настроение → формат, а система сама собирает лучший сценарий поздравления.

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

- [x] CRUD API для получателей (`/api/v1/recipients`)
  - [x] `POST /recipients` — создание
  - [x] `GET /recipients` — список с фильтрацией и пагинацией
  - [x] `GET /recipients/{id}` — детали
  - [x] `PATCH /recipients/{id}` — обновление
  - [x] `DELETE /recipients/{id}` — мягкое удаление (archive)
- [x] Валидация данных (имя обязательно, дата рождения опциональна)
- [ ] Загрузка фото получателя (связь с Assets через `recipient_assets`)
- [x] Поиск и фильтрация по имени, дате рождения, тегам
- [ ] Импорт контактов (CSV/JSON) — *опционально для MVP*

### 1.2 Creative Brief Wizard

- [x] API создания/обновления брифа (`/api/v1/projects/{id}/brief`)
  - [x] `PUT /projects/{id}/brief` — создание/обновление
  - [x] `GET /projects/{id}/brief` — получение текущего состояния
  - [x] `POST /projects/{id}/brief/complete` — завершение заполнения
- [ ] Пошаговая валидация (state machine: `draft → in_progress → completed`)
- [ ] Динамические вопросы на основе `relationship_type` и `occasion`
- [ ] Сохранение черновиков (autosave каждые 30 сек)
- [ ] Предпросмотр заполненного брифа перед отправкой на генерацию

### 1.3 AI Script Generation (Grok Integration)

- [x] Доработка `GrokClient`: промпт-инжиниринг для сценариев
  - [x] System prompt для разных типов поздравлений
  - [x] Structured output (JSON schema enforcement)
  - [x] Temperature tuning для креативности vs консистентности
- [x] Сервис `ScriptGenerationService`:
  - [x] Вход: brief + recipient + template config
  - [x] Генерация 3 вариантов сценария
  - [x] Парсинг ответа Grok в структурированный JSON
  - [x] Валидация длины и содержания
- [x] Celery task `generate_script_task`
  - [x] Retry logic (max 3 attempts, exponential backoff)
  - [x] Timeout handling (60s max per request)
  - [x] Result storage в `generations.output_json`
- [x] API получения результатов (`/api/v1/generations/{id}`)
- [ ] Механизм fallback при ошибке AI (кэшированные шаблоны)

### 1.4 Recommendations Engine (v1)

- [x] Простой scoring algorithm:
  - [x] Match по `occasion_code`
  - [x] Match по `relationship_type`
  - [x] Match по `desired_mood`
  - [x] Weighted score → rank
- [x] API `/api/v1/projects/{id}/recommendations`
  - [x] `GET` — список рекомендаций с объяснениями
  - [x] `POST /select` — выбор шаблона пользователем
- [x] Сохранение выбора в `projects.selected_template_version_id`

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
- [x] Progress tracking через `generation_steps`
  - [x] Real-time status updates
  - [x] ETA calculation
- [x] WebSocket/SSE endpoint для real-time прогресса в UI
  - [x] `GET /api/v1/generations/{id}/stream`

### 2.3 Template Rendering Engine

- [x] Парсинг `template_versions.render_config`
- [x] Подстановка переменных в сцены (`scene_variables`)
  - [x] Text replacement
  - [ ] Image/video insertion
  - [ ] Audio overlay
- [x] Валидация длительности и контента
- [ ] Preview generation (low-res для быстрого просмотра)
  - [ ] 360p preview within 30 seconds
  - [ ] Watermarked

### 2.4 Quality Gate

- [x] Автоматическая проверка:
  - [x] Длина видео (min 15s, max 120s)
  - [x] Разрешение (min 720p)
  - [x] Аудио уровень (no silence, no clipping)
  - [x] FPS consistency
- [x] Ручная модерация финального видео
  - [x] Admin panel для ревью
  - [x] Approve / Reject с комментарием
- [x] Статусы: `rendering → reviewing → approved → rejected`
- [ ] Auto-retry при технических ошибках (не при контентных)

### 🎯 Критерий приёмки Фазы 2

> Пользователь выбирает сценарий → запускает генерацию → видит прогресс → получает готовое видео → смотрит превью.

---

## Фаза 3: Монетизация и Доставка (4–5 недель)

*Цель: Превратить сервис в бизнес — оплата, доставка, шеринг.*

### 3.1 Payment System (YooKassa)

- [x] Создание платежа
  - [x] `POST /api/v1/payments/create`
  - [x] Idempotency key генерация и проверка
  - [x] Расчёт итоговой суммы (price - bonus - promo)
- [x] Webhook обработка
  - [x] `POST /api/v1/payments/webhook/yookassa`
  - [x] Signature verification
  - [x] Idempotent processing
  - [x] Status update + entitlement grant
- [x] Бонусная система
  - [x] Начисление бонусов за покупки (5% cashback)
  - [x] Списывание бонусов (max 30% от суммы)
  - [ ] История транзакций
- [x] История платежей
  - [x] `GET /api/v1/payments` — список
  - [x] `GET /api/v1/payments/{id}` — детали

### 3.2 Delivery System

- [x] Генерация защищённых ссылок
  - [x] Cryptographically secure token
  - [x] Expiration (default 7 days)
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

- [x] Share links с аналитикой просмотров
  - [x] Unique link per share
  - [x] View count tracking
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

- [x] Расчёт цены
  - [x] Base price from template
  - [x] Duration multiplier
  - [x] Personalization premium
  - [x] HD/4K surcharge
- [x] Промокоды
  - [x] Fixed amount / percentage discount
  - [x] Usage limits (per user, total)
  - [x] Expiration date
- [x] Пакетные предложения
  - [x] Bundle: 3 greetings = 15% off
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

## Фаза 5: Аналитика и Growth ✅

*Цель: Data-driven развитие продукта.*

- [x] Analytics pipeline
  - [x] Event collection (`analytics_events` table)
  - [x] ETL to ClickHouse / PostHog
  - [x] Real-time dashboards
- [x] Funnel tracking
  - [x] Visit → Register → Create Project → Complete Brief → Pay → Deliver
  - [x] Drop-off analysis at each step
  - [x] Cohort retention
- [x] A/B testing framework
  - [x] Feature flags
  - [x] Template variants testing
  - [x] Pricing experiments
- [x] Admin dashboard
  - [x] Metabase / Grafana setup
  - [x] Key metrics: DAU, conversion, ARPU, LTV
  - [x] Alerting on anomalies
- [x] Feedback collection
  - [x] In-app NPS survey
  - [x] CSAT after delivery
  - [x] Feature request voting

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
   - [x] MinIO storage adapter
   - [x] YooKassa client
   - [x] `docker compose up` + миграции
   - [x] Health-check тесты

2. **Начать Фазу 1.1: Recipients CRUD** (2 недели)
   - [x] Repository + Service для Recipients
   - [x] API endpoints + Pydantic schemas
   - [x] Unit + integration tests
   - [x] API documentation (OpenAPI)

3. **Параллельно: Grok Prompt Engineering** (ongoing)
   - [x] Тестировать промпты для разных occasions
   - [x] Оценить качество вывода (human eval)
   - [x] Определить optimal temperature / max_tokens
   - [x] Документировать best practices

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
