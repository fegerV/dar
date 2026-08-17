# DarAgent Roadmap

## Goal
Create a clear, execution-ready roadmap from the current state to the first paid user, based on the technical specification v0.2.

## Current State
- Backend MVP implemented: FastAPI, PostgreSQL, Redis, Celery, MinIO, Docker Compose
- UUID-based models, auth, projects, templates, recommendations, payments, generation pipeline, admin API
- 5 seed templates
- README updated and pushed

## Roadmap

### Phase 1: Backend Hardening (Sprint 0-2 equivalent)
**Goal:** Stable, tested backend core ready for client integration

**Deliverables:**
- [ ] Integration tests for auth flow (register/login/refresh/logout)
- [ ] Integration tests for project lifecycle (create → brief → recommendations → template select)
- [ ] Template CRUD API fully functional
- [ ] 5 seed templates validated end-to-end
- [ ] Alembic migrations working (upgrade/downgrade)
- [ ] CI/CD pipeline (GitHub Actions: lint, test, build)
- [ ] API contract stability: Swagger/OpenAPI frozen for mobile

**Exit criteria:** `docker-compose up` starts all services; `/health` and `/api/v1` respond; test suite passes.

---

### Phase 2: Generation Pipeline (Sprint 3-5 equivalent)
**Goal:** End-to-end mock generation from brief to final video asset

**Deliverables:**
- [ ] Prompt Compiler deterministic output validated with golden tests
- [ ] Celery worker queues: script, image, video, voice, render, upload
- [ ] Generation state machine fully implemented with retry logic
- [ ] Quality Gate baseline (MIME, duration, size, required variables)
- [ ] Mock AI providers return deterministic fixtures
- [ ] Final asset stored in MinIO, delivery link created
- [ ] Failure handling: entitlement restore / wallet refund

**Exit criteria:** Full happy-path test: register → recipient → project → brief → recommendations → template → generate → delivery link.

---

### Phase 3: Payments & Monetization (Sprint 7 equivalent)
**Goal:** Real money flow with YooKassa

**Deliverables:**
- [ ] YooKassa integration (create payment, get payment URL)
- [ ] Webhook handler with signature verification and idempotency
- [ ] Wallet ledger mutations only via WalletTransaction
- [ ] First-free-generation entitlement logic
- [ ] Payment → generation start flow automated
- [ ] Admin: payment list, refund action, ledger view

**Exit criteria:** User can pay 699₽ and generation starts automatically after webhook.

---

### Phase 4: Admin & Analytics (Sprint 8 equivalent)
**Goal:** Operational visibility and content management

**Deliverables:**
- [ ] Admin dashboard API (users, projects, generations, payments)
- [ ] Analytics events pipeline (all funnel events)
- [ ] Template versioning: publish/pause/rollback
- [ ] Audit log for admin actions
- [ ] Metrics: conversion, revenue, generation success rate

**Exit criteria:** Admin can see full funnel and regenerate failed generations.

---

### Phase 5: Mobile MVP (Sprint 6 equivalent)
**Goal:** Android app covering the full user flow

**Deliverables:**
- [ ] Auth screens (login/register)
- [ ] Home / Create Greeting flow
- [ ] Recipient selection / creation
- [ ] Brief wizard (occasion, person, mood)
- [ ] Recommendations list
- [ ] Template detail + select
- [ ] Generation status polling
- [ ] Preview + Payment screen
- [ ] My Greetings list
- [ ] Share / Delivery link open

**Exit criteria:** Android user completes full flow from install to share without web UI.

---

### Phase 6: Growth & Polish (Post-MVP)
**Goal:** Viral mechanics and content scale

**Deliverables:**
- [ ] "Answer with greeting" viral loop
- [ ] Recipient cards with history
- [ ] 40 templates catalog
- [ ] Bonus/ledger promotions
- [ ] Push notifications for birthdays
- [ ] Contact import (privacy-first)

---

## Critical Path Dependencies
1. Backend hardening → Mobile can integrate
2. Generation pipeline → Payments can trigger
3. Payments → First paid user milestone
4. Admin/Analytics → Operational readiness before scale

## Definition of Done for MVP
User opens app → creates brief → gets recommendations → selects template → pays → receives final video → shares link. First real payment processed successfully.

## Out of Scope (per spec)
- ML Recommendation Engine
- Social graph / chat
- Built-in video editor
- Marketplace for templates
- iOS / Desktop
- Complex subscription system
- Licensed movie reproductions
