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
