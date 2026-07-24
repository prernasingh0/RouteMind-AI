# Development Guide

## Repository Layout

- `backend/`: FastAPI, Clean Architecture modules, SQLAlchemy, Alembic, Pytest.
- `frontend/`: React 19, Vite, TailwindCSS, Shadcn UI, Vitest, Playwright.
- `shared/`: Cross-service OpenAPI artifacts and shared contracts.
- `infrastructure/`: Docker, Kubernetes, Terraform, deployment manifests.
- `docs/`: Architecture, schema, API, development, and deployment documentation.
- `scripts/`: Developer and CI automation scripts.

## Engineering Standards

- Use dependency injection for infrastructure implementations.
- Keep domain logic free from framework imports.
- Use repositories as application ports and SQLAlchemy implementations as adapters.
- Validate external input at API boundaries with Pydantic or Zod.
- Write migrations for every schema change.
- Add tests with each feature phase.

## Version 1 local validation

Backend dependencies are isolated under `backend/`. Copy `backend/.env.example` to `backend/.env`, set a non-default `SECRET_KEY`, then run Alembic before starting Uvicorn. Frontend configuration uses `frontend/.env` and `VITE_API_BASE_URL`; it must target `/api/v1`.

The operations pages intentionally use only the documented backend endpoints. Populate territories, specialties, HCPs, and addresses before scheduling visits or adding route stops so the optimizer can calculate coordinate-aware travel order.
