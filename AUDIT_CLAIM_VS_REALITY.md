# CLAIM vs REALITY — верификация утверждения «Функциональность полностью реализована»

**Объект проверки:** последние изменения в проекте DarAgent (коммиты `1dbe022`, `2759421`, `272ba86`, `7d9d57e`, а также связанный слой `lab`/`android`).
**Дата проверки:** 2026-09-14
**Метод:** статический анализ + фактический запуск. Поднималось приложение FastAPI (OpenAPI-схема, 207 путей / 239 операций), прогонялся `tsc --noEmit`, запускался `pytest`, сверялись модели ↔ миграции, фронт ↔ backend по методам и путям.

## Вердикт

Утверждение **«функциональность полностью реализована» — НЕ ПОДТВЕРЖДАЕТСЯ**.

Обнаружено, что backend **не запускается на заявленной версии Python** (3.11/3.13), frontend **не проходит сборку типов**, тестовый набор **не запускается вообще** (171 ошибка, 0 пройдено), а из 16 списковых страниц админки **11 не получают данные** из-за расхождения контракта. Ниже — 34 находки в формате CLAIM / REALITY / EVIDENCE / STATUS / FIX.

---

## БЛОК 0. Фатальные блокеры (приложение не работает как заявлено)

### 0.1. Backend не импортируется на Python 3.11/3.13 — заявленный рантайм

- **CLAIM:** функциональность реализована и работоспособна; `requires-python = ">=3.11"`, оба Dockerfile используют `python:3.11-slim`, CI использует `PYTHON_VERSION: "3.11"`.
- **REALITY:** импорт `app.main` падает с `TypeError: 'function' object is not subscriptable`. В теле класса `ProjectService` аннотация `dict[str, list[BriefQuestion]]` вычисляется немедленно, и имя `list` в области видимости класса перекрыто методом `async def list(...)` (строка 58 того же класса).
- **EVIDENCE:**
  - `backend/app/services/projects/service.py:58` — `async def list(`; `:237` — `_RELATIONSHIP_QUESTIONS: dict[str, list[BriefQuestion]] = {`.
  - Трассировка фактического запуска: `TypeError: 'function' object is not subscriptable` при `from app.main import app`.
  - Минимальный воспроизводимый тест: на Python 3.13 → `TypeError`; на Python 3.14 → `CLASS BODY OK` (в 3.14 работает PEP 649 — ленивые аннотации).
  - В репозитории присутствует `app/services/projects/service.cpython-314.pyc` — проект фактически запускался только на 3.14.
- **STATUS:** НЕ РЕАЛИЗОВАНО (приложение не стартует на заявленном рантайме; скрыто тем, что разработка велась на 3.14).
- **FIX:** добавить `from __future__ import annotations` в `app/services/projects/service.py` (и во все модули с подобным перекрытием имён) либо переименовать метод `list` → `list_projects`. Привести `requires-python`, Dockerfile и CI к одной реальной версии.

### 0.2. Объявленных зависимостей недостаточно для запуска

- **CLAIM:** `pip install -e ".[dev]"` даёт рабочее окружение (Dockerfile, CI).
- **REALITY:** в `pyproject.toml` отсутствуют `email-validator` и `prometheus_client`, при этом оба импортируются в runtime-коде.
- **EVIDENCE:**
  - `app/schemas/auth.py:4` — `from pydantic import BaseModel, EmailStr` → без `email-validator`: `ImportError: email-validator is not installed`.
  - `app/services/monitoring/service.py:6` — `from prometheus_client import CONTENT_TYPE_LATEST, ...` → `ModuleNotFoundError: No module named 'prometheus_client'`.
  - `app/core/metrics.py:7` — тот же импорт.
  - `grep -n "email\|prometheus" backend/pyproject.toml` → пусто.
- **STATUS:** НЕ РЕАЛИЗОВАНО (чистая установка по манифесту не даёт запускаемого приложения).
- **FIX:** добавить `pydantic[email]` (или `email-validator`) и `prometheus-client` в `[project].dependencies`.

### 0.3. `Dockerfile.production` ссылается на несуществующий extra

- **CLAIM:** продакшн-образ собирается.
- **REALITY:** `Dockerfile.production` выполняет `pip install -e ".[prod]"`, но в `pyproject.toml` объявлен только extra `dev`. Сборка падает.
- **EVIDENCE:** `backend/Dockerfile.production` — `RUN pip install --no-cache-dir -e ".[prod]"`; `backend/pyproject.toml` — `[project.optional-dependencies]` содержит только `dev`.
- **STATUS:** НЕ РЕАЛИЗОВАНО.
- **FIX:** либо объявить extra `prod`, либо заменить на `pip install -e .`.

### 0.4. Frontend не проходит проверку типов — сборка падает

- **CLAIM:** «Fix TypeScript errors» (коммит `683c8f2`), админка готова.
- **REALITY:** `tsc --noEmit` возвращает exit code 2 и 6 ошибок. CI-шаг `npm run typecheck` и `next build` красные.
- **EVIDENCE:** фактический вывод `./node_modules/.bin/tsc --noEmit`:
  - `src/components/admin/prompts.tsx(194,56): error TS2339: Property 'prompt_id' does not exist on type 'PromptVersion'.`
  - `src/components/admin/rbac.tsx(49,13): error TS2345: Argument of type 'Dispatch<SetStateAction<Record<string, SystemRoleDef>>>' is not assignable to parameter of type '(value: PermissionsResponse) => ...'`
  - `src/i18n/index.ts(79,7)`, `(133,7)`, `(538,12)`, `(564,12): error TS1117: An object literal cannot have multiple properties with the same name.`
- **STATUS:** НЕ РЕАЛИЗОВАНО (артефакт не собирается).
- **FIX:** добавить `prompt_id: string` в интерфейс `PromptVersion`; типизировать `PermissionsResponse` в `rbac.tsx`; удалить дублирующиеся ключи в `src/i18n/index.ts`.

### 0.5. Тестовый набор не выполняется: 171 ошибка, 0 пройденных

- **CLAIM:** AGENTS.md п.13 «All important flows require integration tests», п.17 «Run tests after changes».
- **REALITY:** весь прогон падает на фикстуре. Причина — DSN в `conftest.py`: `sqlite+aiosqlite:///file:test?mode=memory&cache=shared` с `NullPool` даёт `sqlite3.OperationalError: attempt to write a readonly database`.
- **EVIDENCE:**
  - Фактический прогон: `4 warnings, 171 errors in 95.51s`.
  - Контрольный эксперимент: тот же драйвер работает с `sqlite+aiosqlite:///:memory:` → OK, и с файловым путём → OK; падает только на DSN проекта.
  - `backend/tests/conftest.py:25-29`.
- **STATUS:** НЕ РЕАЛИЗОВАНО (заявление «тесты есть» не подтверждается фактом их запуска).
- **FIX:** заменить DSN на `sqlite+aiosqlite:///:memory:` с `StaticPool`, либо использовать файловую БД в `tmp_path`.

---

## БЛОК 1. Очередь и воркеры — «работает в UI, не влияет на систему»

### 1.1. Админ-очередь читает таблицу, которую воркер не обрабатывает

- **CLAIM:** «queue worker filter+pause+detail» — управление очередью реализовано.
- **REALITY:** админка работает с моделью/таблицей `QueueJob` (`queue_jobs`). Реальный воркер обрабатывает **другую** модель — `GenerationJob` (`generation_jobs`). Ни один production-flow не создаёт `QueueJob`.
- **EVIDENCE:**
  - `app/models/admin.py:64` — `class QueueJob ... __tablename__ = "queue_jobs"`.
  - `app/models/generation.py:72` — `class GenerationJob ... __tablename__ = "generation_jobs"`.
  - `app/services/generations/service.py:77,90` — создаётся `GenerationJob` и вызывается `process_generation_job.apply_async(...)`.
  - `app/workers/generation_tasks.py:34` — воркер выбирает `GenerationJob`.
  - `grep -rn "QueueJob" app/` вне `api/v1/admin.py`, `schemas/admin.py` → только модель, репозиторий и сервис админки. Создания нет.
- **STATUS:** НЕ РЕАЛИЗОВАНО (UI админки отображает пустую/постороннюю таблицу; cancel/retry/priority не влияют на реальную генерацию).
- **FIX:** либо перевести воркер и админку на одну сущность, либо синхронизировать `queue_jobs` из `generation_jobs` (проекция), либо явно задокументировать, что это отдельная очередь и наполнять её в `generations/service.py`.

### 1.2. `PATCH /admin/queue/pause` и `/resume` — заглушки

- **CLAIM:** «queue ... pause» — пауза очереди реализована.
- **REALITY:** оба endpoint возвращают константу, ничего не сохраняют и не читаются ни одним воркером. Кнопка «Pause Queue» меняет только локальный state в React.
- **EVIDENCE:**
  - `app/api/v1/admin.py:1762-1775` — `return {"status": "paused"}` / `return {"status": "resumed"}` (нет записи в БД).
  - `grep -rn "paused\|is_paused\|queue_paused" app/` → только строковые литералы ответа и статусы шаблонов, ни одного потребителя флага.
  - `web-app/src/components/admin/queue.tsx:65-74` — переключение локального `queuePaused`.
- **STATUS:** НЕ РЕАЛИЗОВАНО (фиктивная функциональность).
- **FIX:** хранить флаг (например, в `system_settings`) и проверять его в `_process_generation_job` / перед постановкой задач.

### 1.3. `POST /admin/workers/{id}/restart` и `/shutdown` — фиктивное «сигнал отправлен»

- **CLAIM:** «worker logs+params», перезапуск и остановка воркеров.
- **REALITY:** методы только меняют поле `status` в БД и возвращают сообщение «Restart signal sent». Никакого сигнала (Celery control, Redis pub/sub, очередь команд) не отправляется.
- **EVIDENCE:**
  - `app/services/admin/service.py:620-634` — `worker.status = "restarting"`; `return WorkerRestartResponse(success=True, message=f"Restart signal sent to worker {worker.name}", ...)`.
  - Поиск `celery_app.control`, `send_task`, pub/sub по воркерам — отсутствует.
  - `app/services/admin/service.py:624` пишет статус `"restarting"`, который не входит в допустимый набор `WorkerStatusUpdate` (`^(idle|offline|active|maintenance)$`, `schemas/admin.py:371`) — рассогласование модели статусов.
- **STATUS:** НЕ РЕАЛИЗОВАНО.
- **FIX:** реализовать реальный канал управления (Celery `control.broadcast`, отдельная таблица команд) либо честно вернуть `success=False, message="not implemented"`.

### 1.4. `GET /admin/workers/{id}/logs` падает: модели `WorkerLog` не существует

- **CLAIM:** «worker logs» — просмотр логов воркера.
- **REALITY:** endpoint импортирует `from app.models.admin import WorkerLog` — такого класса нет ни в моделях, ни в миграциях. Запрос завершается 500 (`ImportError`).
- **EVIDENCE:**
  - `app/api/v1/admin.py:1785` — `from app.models.admin import WorkerLog`.
  - `grep -rn "WorkerLog\|worker_logs" app/ migrations/` → только это место; класса и таблицы нет.
  - `app/models/admin.py` содержит `Role, UserRole, AdminUser, Worker, QueueJob, SystemSettings, AIProvider, AIModel` — `WorkerLog` отсутствует.
  - Миграция `017_create_admin_tables.py` создаёт `workers` и `queue_jobs`, таблицы `worker_logs` нет.
- **STATUS:** НЕ РЕАЛИЗОВАНО.
- **FIX:** добавить модель `WorkerLog` + миграцию, либо убрать endpoint и блок «Logs» из UI.

### 1.5. Мёртвый код, оставшийся после рефакторинга очереди

- **CLAIM:** рефакторинг списка очереди завершён.
- **REALITY:** в коммите `272ba86` endpoint `list_queue` переписан на inline-запрос, но старый слой остался.
- **EVIDENCE:**
  - `app/services/admin/service.py:302` — `list_queue_jobs` больше не вызывается ниоткуда.
  - `app/repositories/admin.py` — весь модуль не импортируется (`create_queue_job`, `get_queue_job`, `update_queue_job` мертвы).
  - `app/api/v1/admin.py:246-262` — дублирующий inline-запрос вместо сервиса.
- **STATUS:** ЧАСТИЧНО (два параллельных слоя доступа к данным).
- **FIX:** удалить мёртвый слой либо вернуть endpoint на сервис.

---

## БЛОК 2. Frontend ↔ Backend: расхождение контрактов

### 2.1. Массовое расхождение: фронт ждёт `{items,total}`, backend отдаёт массив (11 страниц)

- **CLAIM:** коммит `1dbe022` «feat: add pagination, filters, toasts» — пагинация добавлена.
- **REALITY:** контракт изменён только на фронте. Все компоненты получили `transform`, читающий `raw.items`, но backend переведён на `AdminPaginatedResponse` лишь для 5 из 15 списков. Для массивов `transform` возвращает `undefined`, далее `total = data.length` бросает `TypeError`, который глушится в `catch` → страница показывает ошибку и пустой список.
- **EVIDENCE:**
  - `web-app/src/hooks/use-admin-list.ts:77-89` — ветка `"items" in raw && "total" in raw`, иначе `data = transform(raw); total = data.length`.
  - Одинаковый `transform` в 15 компонентах, напр. `web-app/src/components/admin/queue.tsx:55-58`, `workers.tsx:28-31`, `prompts.tsx:111-114`.
  - Фактические типы ответов по OpenAPI:
    - **`AdminPaginatedResponse` (работает):** `/admin/users`, `/admin/templates`, `/admin/generations`, `/admin/orders`, `/admin/payments`.
    - **массив (ломается):** `/admin/queue`, `/admin/workers`, `/admin/audit-logs`, `/admin/roles`, `/admin/promo-codes`, `/admin/referral-codes`, `/admin/prompts`.
    - **сырой список без схемы (ломается):** `/admin/webhooks`, `/admin/ai/models`, `/admin/support/tickets`.
  - Итого неработающих списков: **11** (включая `moderation` из п.2.2).
- **STATUS:** НЕ РЕАЛИЗОВАНО (для 11 страниц админки данные не отображаются).
- **FIX:** привести ответы перечисленных endpoint'ов к `AdminPaginatedResponse` (или вернуть на фронте ветку для массивов) — но не смешивать оба подхода.

### 2.2. `GET /admin/moderation/items` (список) не существует

- **CLAIM:** «moderation actions» (коммит `2759421`) — модерация реализована.
- **REALITY:** страница запрашивает список модерации, но зарегистрированы только `GET /moderation/items/{item_id}` и `POST /moderation/items/{item_id}/action`. Списка нет → 404.
- **EVIDENCE:**
  - `web-app/src/components/admin/moderation.tsx:46` — `endpoint: "/admin/moderation/items"`.
  - OpenAPI: `/api/v1/admin/moderation/items` — **MISSING**; присутствуют только `['get'] /api/v1/admin/moderation/items/{item_id}` и `['post'] .../action`.
  - `grep` по `admin.py`: ровно два moderation-маршрута.
- **STATUS:** НЕ РЕАЛИЗОВАНО.
- **FIX:** добавить `GET /admin/moderation/items` (или переключить страницу на существующий `/admin/gallery/pending`).

### 2.3. Lab-роутер подключён без префикса: 4 вызова админки → 404

- **CLAIM:** «Video Generation Lab» / страница `/admin/lab` работает.
- **REALITY:** `lab.py` объявлен как `APIRouter()` без префикса и подключён к `/api/v1` — маршруты попали в корень пространства имён. Фронт же зовёт `/api/v1/admin/lab/*`.
- **EVIDENCE:**
  - `app/api/v1/lab.py:25` — `router = APIRouter()` (без prefix).
  - `app/api/v1/router.py:71` — `v1_router.include_router(lab_router)`.
  - OpenAPI: `/api/v1/admin/lab/stats|scenarios|benchmarks|benchmarks/run-all` — **MISSING**; присутствуют `/api/v1/stats`, `/api/v1/scenarios`, `/api/v1/benchmarks`, `/api/v1/photos`, `/api/v1/proposals` (14 операций в корне).
  - `web-app/src/components/admin/lab.tsx:50,62,74,96` — вызовы `/api/v1/admin/lab/...`.
  - Дополнительно: фронт зовёт `/benchmarks/run-all`; в backend есть `run-all` (да) и `run-pending`, но по другому пути.
- **STATUS:** НЕ РЕАЛИЗОВАНО (страница Lab полностью неработоспособна).
- **FIX:** задать `APIRouter(prefix="/admin/lab")` либо добавить проксирующий роутер; убрать 14 маршрутов из корня `/api/v1`.

### 2.4. `GET /admin/templates/{id}` отсутствует — страница сцен не рендерится

- **CLAIM:** «scenes CRUD+drag-drop» (коммит `272ba86`).
- **REALITY:** страница детали шаблона первым делом делает `GET /admin/templates/{templateId}`. Такого маршрута нет и никогда не было (есть только PATCH/DELETE). `Promise.all` реджектится → `template` остаётся `null` → страница возвращает `null` (пустой экран). Весь CRUD сцен и drag-and-drop недостижимы.
- **EVIDENCE:**
  - `web-app/app/admin/templates/[id]/page.tsx:93` — `apiFetch<TemplateDetail>(\`/admin/templates/${templateId}\`)`; `:243` — `if (!template) return null`.
  - OpenAPI: `/api/v1/admin/templates/{template_id}` → `['delete', 'patch']` — GET отсутствует.
  - История: `git show 1dbe022:backend/app/api/v1/admin.py | grep "templates/{template_id}"` → только `@router.patch` и `@router.delete` во всех проверенных коммитах.
  - `grep -n "def get_template" app/services/admin/service.py` → метод отсутствует.
- **STATUS:** НЕ РЕАЛИЗОВАНО (ключевая функциональность последнего коммита недоступна).
- **FIX:** добавить `GET /admin/templates/{template_id}` + `AdminService.get_template`.

### 2.5. Drag-and-drop сцен пишется, но никогда не читается

- **CLAIM:** «scenes ... drag-drop» — порядок сцен сохраняется.
- **REALITY:** `POST /admin/scenes/reorder` пишет `Scene.sort_order`, но **ни один** запрос сцен его не читает: все три места сортируют по `created_at`, а `AdminSceneResponse` не отдаёт `sort_order` фронту. После перезагрузки порядок откатывается.
- **EVIDENCE:**
  - Единственная запись: `app/api/v1/admin.py:1690` — `scene.sort_order = idx`.
  - Чтение: `app/services/admin/service.py:579-580` — `.order_by(Scene.created_at.asc())`; `app/services/templates/renderer.py:120` — `.order_by(Scene.created_at.asc())`; `app/services/prompt_compiler/service.py:177` — без `order_by`.
  - `app/schemas/admin.py:480-495` — `AdminSceneResponse` не содержит `sort_order`, при этом фронт сортирует по нему (`templates/[id]/page.tsx:99,233`).
  - `grep -rn "sort_order" app/` → у сцен только запись, ни одного чтения.
- **STATUS:** НЕ РЕАЛИЗОВАНО (паттерн «файл создан → функция создана → код выглядит правильно → ни один реальный flow её не вызывает»).
- **FIX:** добавить `sort_order` в `AdminSceneResponse` и перевести все запросы сцен на `.order_by(Scene.sort_order.asc())`.

### 2.6. `PATCH /admin/webhooks/{id}` отсутствует — редактирование webhook не работает

- **CLAIM:** управление webhook'ами в админке.
- **REALITY:** фронт вызывает PATCH, backend имеет только `GET /admin/webhooks` и `POST /admin/webhooks`.
- **EVIDENCE:**
  - `web-app/src/components/admin/webhooks.tsx:62-63` — `apiFetch(\`/admin/webhooks/${editing.id}\`, { method: "PATCH" })`.
  - OpenAPI: `/api/v1/admin/webhooks/{webhook_id}` — **MISSING**; присутствует `['get','post'] /api/v1/admin/webhooks`.
- **STATUS:** НЕ РЕАЛИЗОВАНО.
- **FIX:** добавить `PATCH`/`DELETE /admin/webhooks/{id}`.

### 2.7. Возврат платежа: неверный путь и сломанная строка запроса

- **CLAIM:** «payments filters and CSV export» (коммит `2759421`) — операции с платежами.
- **REALITY:** путь `/payments/{id}/refund` без префикса `/admin` → 404. Кроме того, при отсутствии суммы формируется `&reason=...` без `?`, т.е. невалидный URL.
- **EVIDENCE:**
  - `web-app/src/components/admin/payments.tsx:57-59`:
    `const amt = amount ? \`?amount_rub=${amount}\` : ""` → `apiFetch(\`/payments/${id}/refund${amt}&reason=admin_refund\`, { method: "POST" })`.
  - OpenAPI: `/api/v1/payments/{payment_id}/refund` — **MISSING**; существует `/api/v1/admin/payments/{payment_id}/refund` (`['post']`).
- **STATUS:** НЕ РЕАЛИЗОВАНО.
- **FIX:** путь `/admin/payments/${id}/refund?amount_rub=...&reason=...` (корректно собирать `URLSearchParams`).

### 2.8. Impersonation: GET вместо POST → 405

- **CLAIM:** «user IP block+bulk actions» и работа с пользователями в админке.
- **REALITY:** в `users.tsx` вызов impersonate идёт без указания метода → GET, а backend принимает только POST.
- **EVIDENCE:**
  - `web-app/src/components/admin/users.tsx:84-86` — `apiFetch<...>(\`/admin/users/${userId}/impersonate?${new URLSearchParams({...})}\`)` — метод не задан.
  - OpenAPI: `/api/v1/admin/users/{user_id}/impersonate` → `['post']`.
- **STATUS:** НЕ РЕАЛИЗОВАНО.
- **FIX:** указать `{ method: "POST" }`.

### 2.9. SSE-поток админки недоступен: токен не передаётся

- **CLAIM:** коммит `7d9d57e` «fix: correct SSE endpoint indentation in admin.py» — авторизация SSE исправлена.
- **REALITY:** исправлены только отступы. Авторизация по-прежнему не работает: `EventSource` не может задать заголовок, токен в URL не передаётся, а cookie `daragent_admin_access` устанавливается для домена фронтенда и на домен API не отправляется.
- **EVIDENCE:**
  - `web-app/src/hooks/use-admin-events.ts:16-22` — `const url = \`${base}/admin/events/stream-token\`; new EventSource(url)` (без `?token=`).
  - `app/api/v1/admin.py:1343-1348` — токен берётся из `request.query_params.get("token")` или cookie `daragent_admin_access`.
  - `web-app/src/lib/api.ts:23` — cookie ставится через `document.cookie` (домен фронтенда); API — другой origin (`NEXT_PUBLIC_API_URL`, прокси/rewrites в `next.config.*` отсутствуют).
  - `use-admin-events.ts:33-35` — `es.onerror = () => es.close()` — поток молча закрывается.
- **STATUS:** НЕ РЕАЛИЗОВАНО (живые события дашборда не приходят).
- **FIX:** передавать краткоживущий токен в query (`?token=`), получая его через `GET /admin/events/stream-token`, либо проксировать API через Next.js rewrites на тот же origin.

### 2.10. `rbac.tsx`: тип ответа не совпадает с состоянием

- **CLAIM:** «rbac» — страница ролей работает.
- **REALITY:** `GET /admin/rbac/permissions` возвращает `{roles, permissions}`, а результат присваивается состоянию типа `Record<string, SystemRoleDef>`. Ошибка типов + неверная итерация на рантайме.
- **EVIDENCE:**
  - `web-app/src/components/admin/rbac.tsx:48-50` — `.then(setSystemRoles)`.
  - `app/api/v1/admin.py:960-969` — `return {"roles": SYSTEM_ROLES, "permissions": sorted(all_perms)}`.
  - Ошибка `tsc`: `rbac.tsx(49,13): TS2345`.
- **STATUS:** НЕ РЕАЛИЗОВАНО.
- **FIX:** `.then((res) => setSystemRoles(res.roles))`.

---

## БЛОК 3. Модели, миграции, схемы

### 3.1. Таблиц `prompt_templates` / `prompt_template_versions` нет ни в одной миграции

- **CLAIM:** «prompt diff+rollback» (коммит `272ba86`), «prompt template versioning» (`cb19432`).
- **REALITY:** модели `PromptTemplate` и `PromptTemplateVersion` используются в API, но ни одна из 33 миграций их не создаёт. `create_all` в коде отсутствует. На мигрированной БД любой запрос к промптам завершится `UndefinedTableError`.
- **EVIDENCE:**
  - `app/models/template.py:143,161` — `class PromptTemplate` / `class PromptTemplateVersion` (`prompt_templates`, `prompt_template_versions`).
  - `grep -rn "prompt_templates\|PromptTemplate" migrations/` → **пусто**.
  - `grep -rn "create_all" app/ scripts/` → **пусто**; `app/core/lifespan.py` таблицы не создаёт.
  - Сверка «модели ↔ миграции»: таблицы без `create_table` — `prompt_templates`, `prompt_template_versions`.
- **STATUS:** НЕ РЕАЛИЗОВАНО (модуль промптов неработоспособен на реальной схеме).
- **FIX:** добавить миграцию с обеими таблицами (и проверить остальные «осиротевшие» модели).

### 3.2. `holidays.sort_order`: модель есть, колонки нет

- **CLAIM:** справочник праздников работает.
- **REALITY:** модель объявляет `sort_order`, миграция колонку не создаёт, а репозиторий по ней сортирует → `UndefinedColumn`.
- **EVIDENCE:**
  - `app/models/holiday.py:20` — `sort_order: Mapped[int] = mapped_column(Integer, ...)`.
  - `migrations/versions/004_create_holidays.py:20-35` — колонки `sort_order` нет; других миграций по `holidays` нет.
  - `app/repositories/holidays.py:15` — `stmt.order_by(Holiday.sort_order.asc())`.
- **STATUS:** НЕ РЕАЛИЗОВАНО (запросы праздников падают).
- **FIX:** добавить миграцию `ALTER TABLE holidays ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0`.

### 3.3. `ab_tests`: три колонки модели отсутствуют в миграции

- **CLAIM:** A/B-тестирование реализовано.
- **REALITY:** модель `ABTest` содержит `variant_a_id`, `variant_b_id`, `results_lock`; миграция `024_add_ab_testing` их не создаёт → любой запрос к `ABTest` падает.
- **EVIDENCE:**
  - `app/models/ab_test.py:21-23`.
  - `migrations/versions/024_add_ab_testing.py` — `ab_tests` создаётся без этих колонок.
- **STATUS:** НЕ РЕАЛИЗОВАНО.
- **FIX:** добавить миграцию с тремя колонками.

### 3.4. Модели, существующие но не используемые нигде

- **CLAIM:** модели описывают реализованную предметную область.
- **REALITY:** четыре модели не упоминаются за пределами `app/models/`.
- **EVIDENCE:** анализ всех ссылок вне `app/models/`: `ModelProfile` (`intelligence.py`), `RecipeFailure` (`intelligence.py`), `RelationshipType` (`relationship.py`), `TemplateVariable` (`template.py`), `LabStatus` (`lab.py`). Таблицы под них созданы миграциями (`001`, `006`, `016`, `022`).
- **STATUS:** ЧАСТИЧНО (схема есть, логики нет).
- **FIX:** либо реализовать работу с ними, либо удалить вместе с таблицами.

---

## БЛОК 4. Webhooks и платежи

### 4.1. Исходящие webhook'и: диспетчер не вызывается ниоткуда

- **CLAIM:** раздел webhook'ов в админке — функциональность реализована.
- **REALITY:** `dispatch_webhook_event` определён, но не вызывается ни в одном месте. Настроенные webhook-эндпоинты не получат ни одного события.
- **EVIDENCE:**
  - `app/services/webhooks/__init__.py:13` — `async def dispatch_webhook_event(...)`.
  - `grep -rn "dispatch_webhook_event" app/` → единственное вхождение — само определение.
- **STATUS:** НЕ РЕАЛИЗОВАНО (паттерн «функция существует, но её не вызывает ни один flow»).
- **FIX:** вызывать диспетчер из событий (генерация завершена, платёж, доставка) и, желательно, через Celery-задачу.

### 4.2. Обработка webhook'ов в админке «глотает» любые исключения

- **CLAIM:** список webhook'ов стабилен.
- **REALITY:** `GET /admin/webhooks` обёрнут в `try/except Exception: return []`, `GET /admin/support/tickets` — аналогично. Любая ошибка БД/модели превращается в пустой список и маскируется. Это прямо нарушает AGENTS.md п.9 «No silent exception handling».
- **EVIDENCE:**
  - `app/api/v1/admin.py:1174-1185` — `except Exception: return []`.
  - `app/api/v1/admin.py:1414-1438` — `except Exception: return []`.
- **STATUS:** ЧАСТИЧНО / анти-паттерн.
- **FIX:** убрать `except Exception`, логировать и отдавать 500.

### 4.3. Проверка подписи YooKassa несовместима с провайдером

- **CLAIM:** приём платежей реализован, подпись webhook'ов проверяется.
- **REALITY:** проверка требует заголовок `X-Yookassa-Signature` с HMAC-SHA256 по телу. YooKassa так не подписывает уведомления — она аутентифицирует их по списку IP-адресов. В продакшене заголовка не будет → `ValidationException("Invalid webhook signature")` → **ни один платёж не будет подтверждён, кошелёк не пополнится**.
- **EVIDENCE:**
  - `app/api/v1/payments.py:99-105` — `signature = request.headers.get("X-Yookassa-Signature")`.
  - `app/services/payments/service.py:207-211` — `if not signature or not self.yookassa.verify_webhook_signature(...): raise ValidationException("Invalid webhook signature")`.
  - `app/services/payments/service.py:91-102` — HMAC по `YOOKASSA_WEBHOOK_SECRET`.
  - Официальная документация YooKassa (пример обработки уведомлений): фильтрация по IP через middleware; HMAC-подписи нет.
- **STATUS:** НЕ РЕАЛИЗОВАНО / КОНФЛИКТ С ПРОВАЙДЕРОМ (критично для денег).
- **FIX:** реализовать allowlist IP YooKassa (или, как минимум, сделать проверку подписи опциональной при пустом секрете) и добавить идемпотентность обработки уведомлений.

---

## БЛОК 5. Мёртвый код, дубликаты, старые реализации

### 5.1. Два роутера с одним префиксом `/ab-tests`

- **CLAIM:** A/B-тестирование реализовано.
- **REALITY:** `ab_test.py` и `ab_tests.py` — два независимых модуля с одинаковым `prefix="/ab-tests"` и одинаковым тегом, оба подключены в `router.py` (строки 45 и 54).
- **EVIDENCE:** `app/api/v1/ab_test.py:22` и `app/api/v1/ab_tests.py:10` — оба `APIRouter(prefix="/ab-tests", tags=["A/B Testing"])`; `app/api/v1/router.py:45,54`.
- **STATUS:** ДУБЛИРОВАНИЕ (конфликтов путей нет, но модуль раздвоен по смыслу).
- **FIX:** слить в один модуль.

### 5.2. Две реализации планировщика доставки

- **CLAIM:** планирование доставок реализовано.
- **REALITY:** сервис `DeliveryScheduler` не импортируется нигде; его логику дублирует inline-код в Celery-задаче.
- **EVIDENCE:**
  - `app/services/scheduler/delivery.py:17` — `class DeliveryScheduler` (модуль в списке никогда не импортируемых).
  - `app/workers/delivery_tasks.py:33-60` — та же выборка `Delivery.status == "scheduled"` реализована заново.
- **STATUS:** ДУБЛИРОВАНИЕ + мёртвый код.
- **FIX:** оставить одну реализацию (сервис) и вызывать её из задачи.

### 5.3. Две системы метрик

- **CLAIM:** мониторинг реализован.
- **REALITY:** `app/core/metrics.py` (prometheus_client, middleware) не импортируется нигде; `MonitoringService` переопределяет те же метрики заново. При этом обе зависят от незадекларированного `prometheus_client` (см. п.0.2).
- **EVIDENCE:**
  - `app/core/metrics.py` — ни одного импорта (проверено по всем `app/`).
  - `app/services/monitoring/service.py:11-24` — повторное объявление `Histogram/Counter/Gauge` с теми же именами.
  - `app/main.py:147-154` — `/metrics` использует `MonitoringService`.
- **STATUS:** ДУБЛИРОВАНИЕ + неработающий endpoint `/metrics` (500 из-за отсутствующего пакета).
- **FIX:** оставить один модуль метрик, добавить зависимость, покрыть `/metrics` тестом.

### 5.4. Два AI-провайдера: `polza_service.py` не используется

- **CLAIM:** интеграция с AI-провайдерами реализована.
- **REALITY:** `app/integrations/ai/polza_service.py` не импортируется; реестр использует другие провайдеры.
- **EVIDENCE:** модуль в списке никогда не импортируемых; `grep -rn "polza" app/` вне этого файла → только значение `base_url` по умолчанию.
- **STATUS:** МЁРТВЫЙ КОД.
- **FIX:** удалить либо подключить в `registry.py`.

### 5.5. Мёртвый frontend-компонент `order-detail.tsx` с неверными путями

- **CLAIM:** страницы админки реализованы.
- **REALITY:** `src/components/admin/order-detail.tsx` не импортируется ни одной страницей (0 импортёров). Его «двойник» `user-detail.tsx` тоже мёртв и содержит вызовы без префикса `/admin` (`/users/{id}/impersonate`, `/users/{id}/wallet/adjust`) — таких маршрутов нет.
- **EVIDENCE:**
  - Подсчёт импортёров: `order-detail` → 0; при этом в `app/admin/orders/[id]/page.tsx` реализована отдельная страница.
  - `web-app/src/components/admin/user-detail.tsx:65,82` — пути без `/admin`; OpenAPI: `/api/v1/users/{user_id}/wallet/adjust` и `/api/v1/users/{user_id}/impersonate` — **MISSING**.
- **STATUS:** СТАРЫЙ КОД / ДУБЛИКАТ.
- **FIX:** удалить оба неиспользуемых компонента.

### 5.6. Две параллельные сетевые и DI-системы в Android

- **CLAIM:** «feat(android): add repositories and use cases for real API integration» — интеграция с реальным API.
- **REALITY:** в Android сосуществуют два независимых сетевых стека с конфликтующими контрактами, и один из них (подключённый к Hilt) обращается к несуществующим маршрутам.
- **EVIDENCE:**
  - Стек A: `core/network/ApiInterfaces.kt` + `core/network/RetrofitClient.kt` + `core/network/di/NetworkModule.kt` (Hilt), используется в `data/auth/AuthRepository.kt`, `data/people/PeopleRepositoryImpl.kt`, `data/di/RepositoryModule.kt`.
  - Стек B: `data/network/NetworkModule.kt` + `data/network/api/ApiModule.kt` + ручной `di/ServiceLocator.kt`, используется во ViewModel'ях (`HomeViewModel`, `ProfileViewModel`, `CreateGreetingViewModel`, …).
  - Пути стека A против OpenAPI: `/api/v1/users/me`, `/api/v1/people`, `/api/v1/conversations/message`, `/api/v1/briefs`, `/api/v1/media/upload`, `/api/v1/payments/create`, `/api/v1/wallet`, `/api/v1/referrals/code` — **все MISSING** (в backend это `/auth/me`, `/recipients`, `/chat/message`, `/projects/{id}/brief`, `/assets/upload-url`, `/payments/projects/{id}`, `/payments/wallet`, `/referrals/me/code`).
- **STATUS:** НЕ РЕАЛИЗОВАНО / ДУБЛИРОВАНИЕ (две DI-системы, один стек нерабочий).
- **FIX:** оставить один стек (Hilt + корректные пути), удалить второй; вынести базовый URL в `BuildConfig`.

### 5.7. Мёртвая заготовка в `template_versions.py`

- **EVIDENCE:** `app/api/v1/template_versions.py:15-16` — `class VersionUpdateRequest: pass` — пустой класс-заглушка, нигде не используется.
- **STATUS:** ЗАГЛУШКА.
- **FIX:** удалить.

### 5.8. Заглушка `send_message` в bulk-действиях пользователей

- **CLAIM:** «user ... bulk actions» — массовые действия реализованы.
- **REALITY:** для действия `send_message` в цикле стоит `pass`: API возвращает `{"status":"ok","processed":[...]}`, но ничего не отправляется.
- **EVIDENCE:** `app/api/v1/admin.py:1903-1907` — `elif body.action == "send_message": pass`.
- **STATUS:** ЗАГЛУШКА (тихая, с отчётом об успехе).
- **FIX:** реализовать отправку либо исключить действие из допустимого набора.

### 5.9. Блокировка IP пользователя не применяется нигде

- **CLAIM:** «user IP block» — блокировка IP реализована.
- **REALITY:** `blocked_ips` пишется в `user.metadata_` и не читается ни одним middleware/зависимостью. Функция безопасности не имеет эффекта.
- **EVIDENCE:**
  - `app/api/v1/admin.py:1834-1874` — запись/удаление `blocked_ips`.
  - `grep -rn "blocked_ips" app/` вне `admin.py` → **пусто**.
- **STATUS:** НЕ РЕАЛИЗОВАНО (декоративная безопасность).
- **FIX:** проверять `blocked_ips` в middleware (по `request.client.host`) или в `get_current_user`.

### 5.10. `POST /admin/setup` без аутентификации

- **CLAIM:** бутстрап администратора закрыт.
- **REALITY:** endpoint создания первого администратора не требует авторизации (защищён только проверкой «админов ещё нет»). Для конкурирующих запросов проверка не атомарна.
- **EVIDENCE:** `app/api/v1/admin.py:91-101` — `setup_first_admin(body, db)` без `Depends(require_admin)`; `app/services/admin/service.py:106-108` — проверка «count > 0» без блокировки.
- **STATUS:** РИСК (при сбросе/очистке таблицы `admin_users` любой может создать себе админа).
- **FIX:** включать endpoint только при `APP_ENV != production` либо требовать одноразовый bootstrap-токен из переменной окружения.

---

## Сводка по запрошенным категориям

| № | Категория | Находки |
|---|---|---|
| 1 | Заявлено vs реально | Блок 0, 2, 3 — 21 расхождение |
| 2 | Файлы, подключённые в runtime | 34 роутера подключены; 207 путей / 239 операций (OpenAPI) |
| 3 | Файлы, которые существуют но не используются | `app/core/metrics.py`, `app/repositories/admin.py`, `app/integrations/ai/polza_service.py`, `app/services/scheduler/delivery.py`, `web-app/src/components/admin/order-detail.tsx`, `user-detail.tsx` |
| 4 | Функции, которые существуют но не вызываются | `dispatch_webhook_event`, `AdminService.list_queue_jobs`, `DeliveryScheduler.process_due_deliveries`, `create_queue_job`, `VersionUpdateRequest` |
| 5 | Endpoints, существующие но не зарегистрированные | Нет (все 34 роутера подключены); но 14 lab-маршрутов зарегистрированы **вне** ожидаемого префикса |
| 6 | Модели, существующие но не используемые | `ModelProfile`, `RecipeFailure`, `RelationshipType`, `TemplateVariable`, `LabStatus` |
| 7 | Миграции, существующие но не применяемые | `prompt_templates`, `prompt_template_versions` — таблиц нет ни в одной миграции; `holidays.sort_order` и 3 колонки `ab_tests` отсутствуют в миграциях при наличии в моделях |
| 8 | UI-компоненты без вызова API / без данных | 11 списковых страниц (см. п.2.1), `moderation.tsx` (404), `lab.tsx` (404), `templates/[id]` (405 → пустой экран) |
| 9 | API, вызываемые фронтом, но отсутствующие в backend | `/admin/moderation/items`, `/api/v1/admin/lab/*` (4), `/admin/webhooks/{id}` PATCH, `/payments/{id}/refund`, `/users/{id}/wallet/adjust`, `/users/{id}/impersonate`, `GET /admin/templates/{id}` |
| 10 | Зависимости объявленные но не используемые | frontend: `next-auth`, `date-fns`, `@radix-ui/react-dropdown-menu`; backend: `yookassa`, `structlog`, `pillow` (`PIL`), `passlib` |
| 11 | Зависимости используемые но не объявленные | `email-validator`, `prometheus_client` |
| 12 | Заглушки | `queue/pause`, `queue/resume`, `workers/{id}/restart`, `workers/{id}/shutdown`, `send_message`, `VersionUpdateRequest` |
| 13 | Старый код | `user-detail.tsx`, `order-detail.tsx`, `app/core/metrics.py`, `app/repositories/admin.py`, `polza_service.py`, `scheduler/delivery.py` |
| 14 | Дубликаты | `ab_test.py`/`ab_tests.py`, `scheduler/delivery.py`/`delivery_tasks.py`, `metrics.py`/`monitoring/service.py`, два Android-стека, `template_versions.py` vs `admin.py` (версии шаблонов) |
| 15 | Конфликты новой и старой реализации | Android: Hilt-стек A (несуществующие пути) против ServiceLocator-стека B; очередь: `QueueJob` (админка) против `GenerationJob` (воркер) |

---

## Приоритеты исправления

**P0 — блокирует всё:**
1. `from __future__ import annotations` в `app/services/projects/service.py` (п.0.1).
2. Добавить `email-validator` и `prometheus-client` в `pyproject.toml` (п.0.2).
3. Миграция для `prompt_templates` / `prompt_template_versions` (п.3.1).
4. Починить DSN тестовой БД (п.0.5) — иначе регрессии не ловятся.
5. Починить проверку уведомлений YooKassa (п.4.3) — деньги.

**P1 — не работает заявленное:**
6. `GET /admin/templates/{id}` (п.2.4) — открывает весь CRUD сцен.
7. Привести контракты 11 списков к одному формату (п.2.1).
8. Префикс `lab`-роутера + удаление 14 маршрутов из корня (п.2.3).
9. `GET /admin/moderation/items` (п.2.2), `PATCH /admin/webhooks/{id}` (п.2.6).
10. `sort_order` в `AdminSceneResponse` и во всех запросах сцен (п.2.5).
11. Ошибки `tsc` (п.0.4).

**P2 — корректность и чистота:**
12. `holidays.sort_order`, колонки `ab_tests` (п.3.2, 3.3).
13. Реальный pause/restart/shutdown либо честный отказ (п.1.2, 1.3).
14. Модель `WorkerLog` + миграция (п.1.4).
15. Enforcement `blocked_ips` (п.5.9), вызов `dispatch_webhook_event` (п.4.1).
16. Удаление мёртвого кода и дубликатов (блок 5).

---

## Что проверялось фактически (воспроизводимость)

| Проверка | Команда | Результат |
|---|---|---|
| Импорт приложения (3.13) | `python -c "from app.main import app"` | `TypeError: 'function' object is not subscriptable` |
| Импорт приложения (3.14) | то же на Python 3.14 | успешно |
| Реестр маршрутов | `app.openapi()` | 207 путей, 239 операций |
| Типы frontend | `./node_modules/.bin/tsc --noEmit` | exit 2, 6 ошибок |
| Тесты backend | `python -m pytest -q` | 171 error, 0 passed |
| Метрики | `import app.core.metrics` / `monitoring.service` | `ModuleNotFoundError: prometheus_client` |
| Модели ↔ миграции | сверка `__tablename__` и `sa.Column` по всем 33 миграциям | 2 таблицы без `create_table`, 4 колонки отсутствуют |

---

## Статус исправлений (после правок)

Повторная проверка теми же командами:

| Проверка | Было | Стало |
|---|---|---|
| Импорт приложения (3.13) | `TypeError` | **OK** — `IMPORT OK — paths: 210 operations: 244` |
| Тесты backend | `171 error, 0 passed` | **`146 passed` → затем полный прогон зелёный** (см. ниже) |
| Типы frontend | `exit 2, 6 ошибок` | **`tsc --noEmit` — 0 ошибок** |
| Линт backend | — | `ruff check app/ --select F401,F821,F811,F841` — **All checks passed** |

### Исправлено

| № | Находка | Что сделано |
|---|---|---|
| 0.1 | Импорт на 3.11/3.13 | `from __future__ import annotations` в `projects/`, `recipients/`, `recommendations/` |
| 0.2 | Незадекларированные зависимости | добавлены `pydantic[email]`, `prometheus-client`, `starlette`, `aiosmtplib`, `bcrypt` |
| 0.3 | Несуществующий extra `[prod]` | объявлен extra `prod`; удалены неиспользуемые `yookassa`, `structlog`, `pillow`, `passlib` |
| 0.4 | Ошибки `tsc` | `prompt_id` в `PromptVersion`, `res.roles` в `rbac.tsx`, дубликаты ключей i18n удалены |
| 0.5 | Тесты не запускались | `conftest.py`: `:memory:` + `StaticPool`; Celery переведён на `memory://`; добавлена фикстура `async_client`; Docker-тесты пропускаются через `importorskip` |
| 1.1 | Админ-очередь читала `QueueJob` | все queue-endpoint'ы переведены на реальный `GenerationJob` (+ проекция `queue_job_response`) |
| 1.2 | `queue/pause|resume` — заглушки | персистентный флаг в `system_settings` (`app/services/queue_control.py`), воркер его читает |
| 1.3 | Фиктивный restart/shutdown воркера | реальный `control.broadcast`; при недоступности — честный `success=False` |
| 1.4 | `WorkerLog` не существовал | добавлена модель + таблица `worker_logs` (миграция 034) |
| 1.5 | Мёртвый слой репозитория | удалён `app/repositories/admin.py` (вместе с `create_queue_job` и др.) |
| 2.1 | 11 списков ломались | все 11 endpoint'ов → `AdminPaginatedResponse`; **дополнительно исправлен двойной разбор** в `use-admin-list.ts` (хук отдавал `raw.items` в `transform`, который снова читал `.items`) |
| 2.2 | `GET /admin/moderation/items` отсутствовал | зарегистрирован (был мёртвой функцией без декоратора) |
| 2.3 | `lab` без префикса | префикс приведён к `/admin/lab` |
| 2.4 | `GET /admin/templates/{id}` отсутствовал | добавлен endpoint + `AdminService.get_template` |
| 2.5 | `sort_order` сцен не читался | добавлена колонка, поле в `AdminSceneResponse`, сортировка в admin/renderer/prompt_compiler |
| 2.6 | `PATCH /admin/webhooks/{id}` отсутствовал | добавлен PATCH/DELETE |
| 2.7 | Возврат платежа: путь и query | `/admin/payments/{id}/refund` + `URLSearchParams` |
| 2.8 | Impersonation GET вместо POST | `{ method: "POST" }` |
| 2.9 | SSE без токена | токен передаётся в query; `onerror` больше не закрывает поток |
| 2.10 | `rbac.tsx` тип ответа | `.then((res) => setSystemRoles(res.roles))` |
| 3.1 | Нет таблиц промптов | миграция 034: `prompt_templates`, `prompt_template_versions` |
| 3.2 | `holidays.sort_order` | миграция 034 |
| 3.3 | 3 колонки `ab_tests` | миграция 034 (+ типы модели приведены к `Numeric`) |
| 4.1 | `dispatch_webhook_event` не вызывался | вызывается при завершении генерации, платеже и доставке |
| 4.2 | Тихие `except Exception` | удалены в `admin.py` и `webhooks/__init__.py` |
| 4.3 | Подпись YooKassa | allowlist IP (официальные диапазоны) + идемпотентность; HMAC стал опциональным |
| 5.1 | Два роутера `/ab-tests` | слито в `ab_test.py`, `ab_tests.py` удалён |
| 5.2 | Два планировщика доставки | `delivery_tasks.py` делегирует в `DeliveryScheduler` |
| 5.3 | Две системы метрик | `app/core/metrics.py` удалён (в этой ветке мёртв), остался `MonitoringService` — **но при слиянии с `main` файл восстановлен, см. ниже** |
| 5.4 | `polza_service.py` мёртв | удалён (см. «Отложено» — архитектурный конфликт) |
| 5.5 | `order-detail.tsx` / `user-detail.tsx` | `order-detail.tsx` удалён; `user-detail.tsx` **исправлен** (вопреки отчёту, у него есть реальный импортёр `app/admin/users/[id]/page.tsx`) |
| 5.7 | `VersionUpdateRequest` | удалён |
| 5.8 | Заглушка `send_message` | реализована отправка письма |
| 5.9 | `blocked_ips` не применялся | проверка в `get_current_user` |
| 5.10 | `POST /admin/setup` без auth | bootstrap-токен (`X-Bootstrap-Token`) либо запрет в production |

### Найдено дополнительно (не было в исходном отчёте)

- **Обход rate limit.** `app/middleware/rate_limit.py` при недоступности Redis попадал в `except Exception: pass` — счётчик не увеличивался, и лимит логина **молча отключался целиком**. Исправлено: при ошибке Redis используется in-memory fallback.
- **Двойной разбор ответа** в `use-admin-list.ts` (см. п.2.1) — привёл бы к `undefined` во всех 15 списках админки после перевода backend'а на envelope.
- **Ошибка исходного отчёта:** `LabStatus` (п.3.4) **используется** (`app/models/lab.py:75`), удалять его не нужно.

### Отложено (осознанно, с обоснованием)

1. **Android: два сетевых стека (п.5.6).** Это не механическая правка: нужно перевести 7 ViewModel/Screen с `ServiceLocator` на Hilt и одновременно исправить пути к API, затем собрать проект Gradle. Требует Android SDK и проверяемой сборки, которых в этой среде нет (нет ни `java`, ни `ANDROID_HOME`). Переписывание «вслепую» нарушило бы AGENTS.md п.16 и п.18.

   **Частично уже сделано в `main`:** базовый URL вынесен в `BuildConfig` (`build.gradle.kts`: `buildConfigField("String", "API_BASE_URL", ...)` для dev/stage/prod; `RetrofitClient` использует `com.daragent.BuildConfig.API_BASE_URL`). Третий пункт FIX из п.5.6 закрыт.

   **Проверено по факту (сверка 24 endpoint'ов `core/network/ApiInterfaces.kt` с 204 маршрутами backend'а):** не совпадают **18 из 24**. Точная таблица для правки:

   | Android (`core/network/ApiInterfaces.kt`) | Реальный маршрут backend'а | Примечание |
   |---|---|---|
   | `GET /api/v1/users/me` | `GET /api/v1/auth/me` | |
   | `PATCH /api/v1/users/me` | — | endpoint'а обновления профиля нет вообще |
   | `GET /api/v1/people` | `GET /api/v1/recipients` | |
   | `POST /api/v1/people` | `POST /api/v1/recipients` | |
   | `GET /api/v1/people/{id}` | `GET /api/v1/recipients/{recipient_id}` | переименовать path-параметр |
   | `PATCH /api/v1/people/{id}` | `PATCH /api/v1/recipients/{recipient_id}` | переименовать path-параметр |
   | `POST /api/v1/conversations/message` | `POST /api/v1/chat/message` | |
   | `POST /api/v1/briefs` | `PUT /api/v1/projects/{project_id}/brief` | метод и путь |
   | `GET /api/v1/briefs/{id}` | `GET /api/v1/projects/{project_id}/brief` | |
   | `PATCH /api/v1/briefs/{id}` | `PUT /api/v1/projects/{project_id}/brief` | метод и путь |
   | `POST /api/v1/media/upload` | `POST /api/v1/assets/upload-url` | далее `POST /assets/confirm-upload` |
   | `POST /api/v1/generations` | `POST /api/v1/generations/projects/{project_id}` | |
   | `GET /api/v1/generations` | `GET /api/v1/generations/projects/{project_id}` | |
   | `POST /api/v1/payments/create` | `POST /api/v1/payments/projects/{project_id}` | |
   | `GET /api/v1/payments` | — | списка платежей нет (только `/{payment_id}`, `/entitlements`) |
   | `GET /api/v1/wallet` | `GET /api/v1/payments/wallet` | |
   | `GET /api/v1/referrals` | `GET /api/v1/referrals/me/stats` | ближайший существующий |
   | `GET /api/v1/referrals/code` | `GET /api/v1/referrals/me/code` | |

   Совпадают (не требуют правки): `POST /auth/login`, `POST /auth/register`, `POST /auth/refresh`, `GET /generations/{id}`, `GET /payments/{id}`.

   Оставшийся план: исправить пути выше → удалить `data/network/*` + `di/ServiceLocator.kt` → перевести 7 потребителей на `core/network` (Hilt) → собрать Gradle.
2. **4 неиспользуемые модели (п.3.4): `ModelProfile`, `RecipeFailure`, `RelationshipType`, `TemplateVariable`.** Их таблицы реально существуют (миграции 001/006/016), запись в них не ведётся ни одним flow. Удаление моделей требует DROP TABLE — необратимая операция над схемой, поэтому в рамках этого прохода не выполнялось. Зафиксировано как известный долг.
3. **`QueueJob`.** После перевода админки на `GenerationJob` таблица `queue_jobs` (миграция 017) больше не используется, но не удаляется по той же причине — помечена как legacy в docstring модели.

### Уточнение: расхождение версий Python в CI не является дефектом

Пункт 0.1 рекомендовал «привести `requires-python`, Dockerfile и CI к одной версии». Проверка показала,
что приводить нечего:

- `requires-python = ">=3.11"`, оба `Dockerfile` — `python:3.11-slim`, `ci-cd.yml` — `PYTHON_VERSION: "3.11"`
  → **заявленный минимум 3.11 реально тестируется**;
- `ci.yml` использует 3.12 — это не рассинхрон, а **дополнительное покрытие** второй версии;
- `ci.yml` не является дублем `ci-cd.yml`: его `build` собирает Docker-образ **на pull request'ах**, а в
  `ci-cd.yml` build и deploy ограничены `if: github.ref == 'refs/heads/main'`, то есть на PR образ не
  проверяется. Поэтому удалять `ci.yml` не следует — он даёт единственную проверку сборки образа до мержа.

Оставляю как есть: объединение pipeline'ов — решение владельца репозитория, а не исправление ошибки.

---

## Слияние с `origin/main` (коммит `9539c2d`, ветка `merge/audit-fixes-into-main`)

Ветка с правками разошлась с `origin/main` на 548 файлов. Конфликты определены через
`git merge-tree --write-tree` (read-only, без чекаута): **всего 3 конфликтующих файла**,
остальные 4 (`admin.py`, `payments/service.py`, `models/__init__.py`, `rbac.tsx`) слились автоматически.

| Файл | Решение |
|---|---|
| `app/middleware/rate_limit.py` | Взят вариант `main`: он богаче (лимиты по endpoint, sliding window на Redis sorted set, счётчики Prometheus) и **уже содержит** in-memory fallback при падении Redis — то есть нужный фикс там реализован независимо |
| `app/workers/generation_tasks.py` | Оставлено делегирование `main` в `execute_pipeline`, поверх него возвращена проверка паузы очереди (`is_queue_paused`) перед передачей задачи |
| `pyproject.toml` | Объединение: возвращён `structlog` (нужен `core/logging_config.py` на `main`); `passlib`, `yookassa` и `pillow` удалены — подтверждено, что они не импортируются (`bcrypt` импортируется напрямую) |

### Ошибка исходного отчёта №2: `core/metrics.py` удалять нельзя

Находка 5.3 рекомендовала удалить `app/core/metrics.py` как мёртвый код — и на **этой** ветке он действительно
мёртв (0 импортов). Но в `main` его уже используют `core/exception_handlers.py` и
`middleware/rate_limit.py` (импортируют `http_requests_total`). Удаление в процессе слияния привело бы к
`ImportError` при старте приложения. Файл **восстановлен** в мерж-коммите.

Практический вывод: «мёртвый код» нужно проверять не только по своей ветке, но и по целевой ветке слияния.

### Проверка миграции 034 выполнением

Ранее миграция была проверена только сверкой колонок. Теперь проверена рендерингом без подключения к БД:

```
alembic upgrade 033_ai_providers_models:034_admin_template_fixes --sql
```

→ 13 корректных DDL-операторов PostgreSQL: `ALTER TABLE scenes/holidays/ab_tests`,
`CREATE TABLE prompt_templates`, `prompt_template_versions`, `worker_logs` и индексы к ним.
