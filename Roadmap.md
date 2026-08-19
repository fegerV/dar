# 🗺️ DarAgent — Product & Tech Roadmap

> AI-сервис персональных видеопоздравлений  
> Last updated: 2026-08-18

---

## Обзор

DarAgent — не генератор видео, а **система создания персональных мини-фильмов**. Главная задача: получить от пользователя фотографию + смысл поздравления → превратить пользователя в героя → согласовать сценарий → сгенерировать видео → добавить голос, VFX и финальную надпись → выдать эмоциональный результат, который запомнят.

```
USER
  │
  ▼
Upload Photo
  │
  ▼
AI PHOTO ANALYSIS
  │
  ├─ BAD PHOTO → Fix/Reject
  │
  ▼
IMAGE GENERATION 1 — New Look / New Scene
  │
  ▼
MASTER FRAME PREVIEW
  │
  ├─ "✨ Удиви меня" → 3 cinematic concepts
  │
  ▼
USER CHOOSES CONCEPT
  │
  ▼
RECIPIENT / OCCASION / MOOD
  │
  ▼
AI VIDEO SCRIPT
  │
  ▼
VIDEO GENERATION 2 — Motion / Mimic / Camera / VFX
  │
  ▼
VOICE + TEXT OVERLAY + FINAL COMPOSITING
  │
  ▼
VIDEO QUALITY GATE
  │
  ├─ PASS → USER
  │
  ▼
FAIL → FAILURE ANALYZER
  │
  ▼
PROMPT REPAIR ENGINE
  │
  ▼
TARGETED REGENERATION
```

**Текущий статус:** Фазы 0–2.4, 3.1–3.3 и 5 выполнены. Закрытие пробелов из ДарАГЕНТ.txt. Добавлен Intelligence Core: Image Preflight, Video Recipes, Prompt Repair, Failure Analyzer, targeted regeneration. Границы MVP зафиксированы в [ТЗ_MVP.md](./ТЗ_MVP.md) — разделение на Lite Greeting (6 сек, вирусный, 3 бесплатно/мес) и Premium (cinematic mini-film c утверждением master frame).

**Ключевой принцип MVP:** Пользователь не создаёт контент с нуля. Он загружает фото → Дарагент превращает его в героя → выбирает готовый концепт/сцену → согласовывает сценарий → только после этого запускается дорогая видеогенерация.

---

## Архитектура генерации: 2 этапа

Вместо одного shot-in-the-dark video generation:

1. **Image Generation 1** — создаём **master frame** (идеальный ключевой кадр): новый образ пользователя + новая сцена + кинематографический свет.
2. **Video Generation 2** — оживляем master frame: движение, мимика, жесты, камера, спецэффекты, речь, финальная надпись.

Плюс отдельные ингредиенты:
- **TTS** — голос
- **VFX engine** — частицы, искры, сияние, конфетти
- **Compositor** — финальная надпись/титры

Финал: `IMAGE → VIDEO → VOICE → VFX → TEXT OVERLAY → FINAL RENDER`

## Онбординг и сценарий создания

- **Splash → Welcome → Auth (phone/SMS) → About Me (gender/age) → Photos → Quality Check → Home**
- **Home:** нижняя навигация Главная / История / Фото / Профиль
- **Новое поздравление (wizard):**
  1. Кого поздравляем?
  2. Профиль получателя (имя, возраст, прозвище)
  3. Повод
  4. Отношения + черты характера (теги)
  5. Интересы + заметки
  6. Настроение (До слёз / До смеха / Вау! / Стильно / Как кино / Необычно)
  7. **✨ Удиви меня** — Дарагент предлагает 3 готовых cinematic concepts на основе данных пользователя/получателя
  8. Текст поздравления (редактировать/перегенерировать/оставить)
  9. Шаблон/визуальный концепт
  10. Финальный обзор
  11. Оплата/бонусы
  12. Генерация (прогресс)
  13. Результат + Share
  14. Рейтинг/отзыв

## Отдельная воронка: «Примерить образ»

Кнопка на главном экране: **✨ Примерить образ**.
Бесплатно/дёшево делает Image Generation 1, не создавая полного поздравления.
После получения master frame:
- **Оживить этот образ** → переход в полноценный wizard поздравления.
Самостоятельная воронка продаж.

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

## Фаза 1: MVP Core — «От Фото до Скрипта» (4–6 недель)

*Цель: Пользователь может загрузить фото, получить master frame и персонализированный текстовый сценарий.*

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

### 1.2 AI Photo Analysis & Image Generation 1

- [x] Preflight анализ фото
  - [x] Quality score, face count, pose, sharpness
  - [x] Recommend models/templates
- [x] Image Generation 1 — master frame
  - [x] Новый образ пользователя (новый look)
  - [x] Новая сцена (фон, атмосфера, свет)
  - [x] Провайдеры: OpenAI DALL-E 3, Flux, Stable Diffusion
- [x] Master Frame Preview
  - [x] Пользователь утверждает кадр перед дорогой видеогенерацией
  - [x] **✨ Удиви меня** — 3 готовых cinematic concepts

### 1.3 Creative Brief Wizard

- [x] API создания/обновления брифа (`/api/v1/projects/{id}/brief`)
  - [x] `PUT /projects/{id}/brief` — создание/обновление
  - [x] `GET /projects/{id}/brief` — получение текущего состояния
  - [x] `POST /projects/{id}/brief/complete` — завершение заполнения
- [ ] Пошаговая валидация (state machine: `draft → in_progress → completed`)
- [ ] Динамические вопросы на основе `relationship_type` и `occasion`
- [ ] Сохранение черновиков (autosave каждые 30 сек)
- [ ] Предпросмотр заполненного брифа перед отправкой на генерацию

### 1.4 AI Script Generation (Grok Integration)

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

### 1.5 Recommendations Engine (v1)

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

### 2.1 Image Generation 1 — Master Frame

- [x] AI Photo Analysis (preflight)
  - [x] Quality score, face count, pose, sharpness
  - [x] Recommend models/templates
- [x] Image Generation 1
  - [x] Новый образ пользователя (новый look)
  - [x] Новая сцена (фон, атмосфера, свет)
  - [x] Master frame — идеальный ключевой кадр
  - [x] Провайдеры: OpenAI DALL-E 3, Flux, Stable Diffusion
- [x] Master Frame Preview
  - [x] Пользователь утверждает кадр перед дорогой видеогенерацией
  - [x] **✨ Удиви меня** — 3 готовых cinematic concepts
- [x] Asset Management System
  - [x] Storage abstraction layer
  - [x] Upload API с presigned URLs
  - [x] Проверка файлов
  - [x] CDN-friendly URL generation

### 2.2 Video Generation 2 — Motion & VFX

- [x] Оркестратор пайплайна (Celery canvas / chain):
  ```
  master_frame_approved
    → video_generation (motion/mimic/camera)
    → voice_synthesis (TTS)
    → vfx_engine (частицы/искры/сияние/конфетти)
    → compositor (текст/титры/финальная надпись)
    → final_render
    → upload_final
  ```
- [x] Интеграция с Video AI
  - [x] HeyGen API (primary)
  - [x] D-ID API (fallback)
  - [x] SadTalker self-hosted (cost optimization)
- [x] TTS
  - [x] Yandex SpeechKit (primary)
  - [x] ElevenLabs (fallback/premium)
- [x] VFX engine
  - [x] Particles, sparks, glow, confetti
  - [x] Text overlay / final title
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
  - [x] Техническая проверка: длительность, разрешение, fps, audio, codec
  - [x] Визуальная проверка: лица, деформации, артефакты, landmarks, blink
  - [x] Семантическая проверка: prompt adherence, scene classifier
  - [x] Video Critic: identity/motion/face_quality/prompt_adherence/artifact scores
- [x] Ручная модерация финального видео
  - [x] Admin panel для ревью
  - [x] Approve / Reject с комментарием
- [x] Статусы: `rendering → reviewing → approved → rejected`
- [x] Auto-retry при технических ошибках (не при контентных)
  - [x] До 3 попыток перед показом пользователю

### 2.5 Intelligence Core — «Ядро Дарагента»

- [x] Image Preflight
  - [x] Проверка разрешения, лица, размера лица, резкости, позы
  - [x] Определение проблем: закрытые глаза, профиль, несколько людей, освещение
  - [x] Рекомендация моделей и шаблонов на основе входного фото
  - [x] `POST /api/v1/intelligence/preflight`
- [x] Video Recipes
  - [x] База проверенных сценариев: template + model + prompt + negative strategy
  - [x] Учёт success rate, avg_generations, cost_estimate
  - [x] Known failures per recipe с рекомендациями по исправлению
  - [x] `GET /api/v1/intelligence/recipes/{code}`
- [x] Prompt Repair Engine
  - [x] Mapping: failure_code → targeted prompt/negative repair
  - [x] Целенаправленная регенерация вместо случайного ретрая
  - [x] Снижение среднего количества генераций с 3–5 до 1.15–1.4
- [x] Failure Analyzer
  - [x] Анализ critic scores + quality checks → failure_codes
  - [x] `GET /api/v1/intelligence/generations/{id}/failure`
- [x] User Feedback Loop
  - [x] Сбор rating/reason/comment после просмотра
  - [x] `POST /api/v1/intelligence/feedback`
- [x] Model Selector
  - [x] Выбор модели на основе recipe + input metadata
  - [x] Fallback стратегия при отсутствии recipe
- [x] Targeted Regeneration
  - [x] При FAIL → Prompt Repair → Regeneration с исправленным prompt
  - [x] Сохранение GenerationFailure с repaired_prompt/negative/model

### 2.6 Video Generation Lab (experimental)

- [ ] Структура БД и админки для лаборатории
- [ ] Загрузка тестовых фотографий (20–50 шт.)
- [ ] Benchmark: 15 сценариев × 3–4 модели = 60 экспериментов
- [ ] Автоматические оценки: cost, quality, success rate, avg_generations
- [ ] Формирование Recipe/Model Profile → production

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
  - [x] Max views limit
  - [x] Optional password protection
- [x] Email delivery
  - [x] SMTP integration
  - [x] HTML email templates
  - [x] Tracking pixel
- [x] Telegram Bot delivery
  - [x] Bot API integration
  - [x] Inline keyboard with actions
  - [x] Video as document (no compression)
- [x] Scheduled delivery
  - [x] Отложенная отправка к указанной дате/времени
  - [x] Timezone-aware scheduling
  - [x] Cancel/reschedule

### 3.3 Воронка продаж: «Примерить образ»

- [x] Image Generation 1 как отдельная услуга
  - [x] Бесплатно/дёшево master frame без полного поздравления
  - [x] Кнопка «Оживить этот образ» → переход в wizard
- [x] Финальная надпись как отдельный объект
  - [x] Не полагаемся на video-model для текста
  - [x] Compositor накладывает титры после генерации

### 3.4 Sharing & Virality

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

- [x] Responsive Web App (PWA-ready)
  - [x] Mobile-first design
  - [x] Service worker для offline
  - [x] Install prompt
- [x] Onboarding flow
  - [x] Splash / Welcome / Auth (phone+SMS)
  - [x] About Me (gender/age)
  - [x] Photo upload + quality check
  - [x] Home with bottom nav (Главная/История/Фото/Профиль)
- [x] Новое поздравление (wizard)
  - [x] Кого? / Получатель / Повод / Отношения / Интересы / Настроение
  - [x] **✨ Удиви меня** — 3 AI cinematic concepts
  - [x] Текст (редактировать/перегенерировать)
  - [x] Шаблон/визуальный концепт
  - [x] Финальный обзор / Оплата / Генерация / Результат / Share / Рейтинг
- [x] **✨ Примерить образ** (воронка продаж)
  - [x] Image Generation 1 master frame без полного поздравления
  - [x] Кнопка «Оживить этот образ» → переход в wizard
- [x] Dashboard
  - [x] Мои проекты (active, completed, archived)
  - [x] История покупок
  - [x] Избранные получатели
  - [x] Quick actions
- [x] Редактор сценария
  - [x] Post-generation text editing
  - [x] Regenerate specific sections
  - [x] Version history
- [x] Push-уведомления
  - [x] Web Push API
  - [x] Telegram notifications
  - [x] Email digest (weekly)
- [x] Accessibility (a11y)
  - [x] WCAG 2.1 AA compliance
  - [x] Screen reader support
  - [x] Keyboard navigation
- [x] i18n подготовка
  - [x] String extraction
  - [x] EN/RU translation
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

## Фаза 4.5: Admin — Operational Center (2–3 недели)

*Цель: Управление продуктом как фабрикой поздравлений, а не CRUD.*

- [x] RBAC + Admin Users
  - [x] `is_admin` на `User`
  - [x] Роли: Owner, Admin, Content Manager, Support, AI Operator, Analyst, Moderator
  - [x] Аудит действий
- [x] Dashboard
  - [x] Users / Orders / Generations / Revenue / AI Cost / Profit
  - [x] Running / Queued / Failed jobs
  - [x] GPU / Workers heartbeat
- [x] Orders
  - [x] Таблица заказов с фильтрами
  - [x] Карточка заказа: input, prompt, generation, output, timeline, margin
- [x] Generations
  - [x] Все попытки генерации
  - [x] Model / Workflow / Prompt version / Seed / Cost / Duration
- [x] Queue
  - [x] Running / Pending / Failed
  - [x] Pause / Retry / Cancel / Priority controls
- [x] Users + Wallet
  - [x] Сегменты
  - [x] Ledger operations (только ledger, не прямой edit баланса)
  - [x] Impersonate с audit log
- [x] Templates + Content
  - [x] Template editor с scenes / variables / conditions
  - [x] Prompt Library
- [x] Payments
  - [x] Платежи + Ledger
  - [x] Webhooks
- [x] AI / Workers
  - [x] Workers heartbeat
  - [x] GPU / VRAM / Jobs
- [x] System
  - [x] Logs / Audit / Settings

---

## 🕳️ Пробелы из ДарАГЕНТ.txt

*Ниже — расширение Roadmap до полного соответствия технической спецификации.*

### Backend / Domain

- [x] Calendar Engine — календарь праздников, профессиональных дней, персональных событий + automatic Today Pack
- [x] Relationship Context — расширенные типы отношений, subtypes, grupos/circles, inside jokes, shared memories
- [x] Prompt Compiler — детерминированный компилятор `Template + Creative Brief + Scene → provider prompt`
- [x] Template Conditions — IF/ELSE по `recipient.age`, `relationship`, `occasion` и другим полям
- [x] Template Versioning & QA — версии, статусы `draft/testing/published/paused/archived`, обязательный QA-чеклист
- [ ] 40 начальных шаблонов — каталог по категориям с карточками, себестоимостью и метриками
- [x] First Generation Free — `welcome_generation_credit`, отдельный entitlement type
- [x] Bonus System Details — пятничный бонус, бонусы за действия, expiry, конфигурируемые через Admin
- [x] Detailed Admin Panel — Users, Projects, Generations, Payments, Templates, Referrals, Audit
- [x] Security Events & Audit Log — `audit_logs` + `admin_users` + actions (AuditMiddleware → DB)
- [x] Backup Strategy — daily full backup, WAL/PITR, offsite, retention
- [x] Production Security — Cloudflare, firewall, SSH, non-root Docker, secrets management
- [x] Disaster Recovery — RTO/RPO, recovery runbook, tested restore
- [x] Health/Disk Monitoring — Prometheus + alerts on disk/CPU/memory/queue depth
- [x] Account Deletion — GDPR export, hard delete, anonymization

### Product / Growth

- [x] Contact Import — локальная обработка контактов, явный выбор, privacy-first
- [x] Scheduled Delivery — отложенная отправка к дате/времени, timezone-aware
- [x] Referral Program — `referral_codes`, `referrals`, бонусы за invite/registration
- [x] Telegram Bot — acquisition/распространение через Telegram, deep links, Mini App-ready backend
- [ ] Android App — Kotlin/Jetpack Compose, Clean Architecture, основное клиентское приложение
- [x] Feedback Loop — пост-просмотровые реакции (`🔥/❤️/😂/😭/😐`), детали негатива
- [x] A/B Testing Framework — варианты шаблонов/цен/скриптов, сравнительные метрики

---

## Фаза 6: Масштабирование и Безопасность (Параллельно)

### Security

- [x] Rate limiting (per IP, per user) — Redis-backed with in-memory fallback
- [x] Input sanitization (XSS, SQL injection)
- [x] Audit logs для критических действий — AuditMiddleware writes to DB
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
- [MVP Specification — границы Lite / Premium](./ТЗ_MVP.md)
- [API Documentation](./docs/api.md) *(TODO)*
- [Architecture Decision Records](./docs/adr/) *(TODO)*
- [Figma Designs](https://figma.com/file/xxx) *(TODO)*
- [Notion Board](https://notion.so/xxx) *(TODO)*

---

*Этот документ является живым и обновляется по мере развития проекта. Последнее обновление: 2026-08-17.*
