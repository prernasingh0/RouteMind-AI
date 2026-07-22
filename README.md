# RouteMind AI

RouteMind AI is an enterprise-grade, AI-powered assistant for pharmaceutical sales representatives. It supports field representatives before, during, and after healthcare professional visits by improving visit planning, doctor engagement, route optimization, and CRM automation.

## Phase 1 Scope

This repository currently contains the Phase 1 production architecture foundation:

- Clean Architecture and Domain-Driven Design blueprint
- Enterprise folder structure for frontend, backend, shared contracts, and infrastructure
- Multi-tenant normalized PostgreSQL schema design
- Dynamic doctor priority scoring model
- Mermaid architecture and ER diagrams
- Development, deployment, and API documentation stubs with concrete conventions

## Target Stack

- **Frontend:** React 19, TypeScript, Vite, TailwindCSS, Shadcn UI, React Query, React Router, Framer Motion, React Hook Form, Zod, Axios, Chart.js
- **Backend:** Python, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2
- **AI:** LangGraph, LangChain, OpenAI, Azure OpenAI, Structured Outputs, Tool Calling
- **Data:** PostgreSQL, Redis, S3-compatible object storage
- **Security:** JWT, refresh tokens, RBAC, audit logs, organization isolation
- **Delivery:** Docker, Docker Compose, GitHub Actions
- **Testing:** Pytest, Playwright, Vitest

## Documentation

- [Architecture](docs/architecture/architecture.md)
- [Database Schema](docs/database/schema.md)
- [ER Diagram](docs/database/er-diagram.md)
- [API Design](docs/api.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)

## Delivery Phases

1. Architecture, folder structure, database schema, ER diagram
2. Backend setup, authentication, infrastructure
3. Frontend foundation, theme, routing, components
4. Doctor module
5. Visit module
6. AI agents
7. LangGraph orchestration
8. Route planner
9. Analytics
10. Testing
11. Docker
12. CI/CD


## Phase 2 Backend Foundation

The backend is a runnable FastAPI service located in `backend/`. It includes SQLAlchemy 2 async database access, Alembic migrations, PostgreSQL and Redis configuration, JWT access/refresh-token authentication, RBAC dependency helpers, structured logging, request/error middleware, Docker support, and pytest authentication coverage.

### Local backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

The API is served at `http://localhost:8000`, OpenAPI docs at `/docs`, and versioned endpoints under `/api/v1`.

### Docker Compose

```bash
docker compose up --build
```

Compose starts PostgreSQL, Redis, runs Alembic migrations, and serves the FastAPI application on port `8000`.

### Backend tests

```bash
cd backend
pytest
```

Authentication tests use an in-memory SQLite database and exercise login, refresh, logout, and authenticated `/auth/me` flows.

## Phase 3 Business Domain Backend

Phase 3 adds the core RouteMind AI business backend without frontend or AI-agent work. The API now exposes tenant-isolated CRUD endpoints under `/api/v1` for regions, territories, doctors, specialties, addresses, products, product categories, product priority rules, campaigns, visits, visit notes, call objectives, recommendations, interactions, routes, route stops, calendar events, activities, attachments, notifications, and settings.

All business tables are organization-owned, use UUID primary keys, timestamps, soft deletes, indexes, and foreign keys. API routes delegate business behavior to service classes and repository classes built on the generic repository foundation.

Doctor priority is calculated dynamically and is not persisted on the doctor record. Use `GET /api/v1/doctors/{doctor_id}/priority` to retrieve the total score, classification, and per-strategy factor breakdown. The priority engine uses Strategy Pattern rules for days since last visit, visit frequency, campaign weight, product priority, missed visits, manager adjustments, and territory targets.

## Phase 4 AI Orchestration Backend

Phase 4 adds the backend AI orchestration layer under `backend/app/ai` without frontend work. The AI layer is separated into graphs, agents, tools, prompts, memory, models, parsers, extractors, services, schemas, callbacks, and utilities.

The default model provider is OpenAI, selected through `LLM_PROVIDER=openai`, with Azure OpenAI support available through the provider factory. Business logic depends on the `LLMProvider` abstraction so future Anthropic, Gemini, or local model providers can be added without changing agents or services.

RouteMindGraph orchestrates supervisor, intent detection, tool selection, memory retrieval, response generation, structured output validation, and conversation summary nodes. AI endpoints are exposed under `/api/v1/ai`, including chat, streaming chat, pre-call planning, post-call extraction, summaries, route planning, doctor search, and conversation management.


## Phase 5 Frontend Foundation

The frontend is a React 19, TypeScript, Vite, TailwindCSS, Shadcn-style component foundation located in `frontend/`. It consumes the FastAPI backend through Axios clients under `src/api`, persists JWT sessions, refreshes access tokens automatically, and uses TanStack Query for server state.

Run locally:

```bash
cd frontend
npm install
npm run dev
```

Build and test:

```bash
cd frontend
npm run build
npm test
npm run test:e2e
```

The application shell includes protected routing, login/logout, sidebar navigation, top navigation, notification entry point, dark mode, global error boundary, offline status, backend-driven dashboard queries, and a reusable AI chat experience backed by `/api/v1/ai/chat`.

## Phase 6 Doctor Management Module

The Doctor/HCP module adds backend doctor management APIs and frontend doctor workflows. Backend endpoints under `/api/v1/doctors` support doctor CRUD, specialty/address-compatible profile data, contact information, territory/region assignment, product and campaign associations, visit history, AI conversation history hooks, attachments, notes, tags, active/inactive status, pagination, sorting, filtering, global search, soft delete, bulk operations, CSV import, and CSV export.

Doctor profile and timeline endpoints consolidate visits, notes, recommendations, product/campaign associations, attachments, priority snapshots, notifications, and priority score explanations. The priority engine now records historical score snapshots and supports what-if simulation through `/doctors/{id}/priority/history` and `/doctors/{id}/priority/simulate`.

The frontend adds `/doctors`, `/doctors/new`, `/doctors/:id`, and `/doctors/:id/edit` routes with a server-driven doctor table, filters, bulk actions, CSV export, profile tabs/sections, visualizations, priority breakdowns, timeline, and AI action buttons connected to the existing AI chat API.

## Version 1 operational modules

Version 1 completes the field workflow around the existing doctor and AI capabilities:

- **Visits**: schedule, reschedule, complete/cancel, capture outcomes and follow-ups, add notes, and retrieve a tenant-scoped visit timeline at `/api/v1/visits`.
- **Routes**: create routes with ordered stops and run provider-neutral nearest-neighbour optimization at `/api/v1/routes/{route_id}/optimize`. Coordinates are read from doctor addresses; no map vendor integration is required.
- **Calendar**: retrieve the authenticated representative's visits and calendar events over a validated time range through `/api/v1/calendar`.
- **AI**: pre-call and post-call flows remain under `/api/v1/ai`; post-call capture now completes its linked visit and records the source note.

Run backend checks with `cd backend && SECRET_KEY=... python -m compileall app tests alembic`; run the full test suite with `python -m pytest` after installing `requirements-dev.txt`. Run frontend checks with `cd frontend && npm ci && npm run build && npm test`. Docker Compose starts PostgreSQL, Redis, the backend migration/start command, and the frontend: `docker compose up --build`.
