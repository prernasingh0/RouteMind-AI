# Deployment Guide

RouteMind AI is designed for Docker Compose during local development and containerized production deployment.

## Production Components

- React static web app served by an edge/runtime web server.
- FastAPI application served by ASGI workers.
- PostgreSQL primary database.
- Redis for caching, rate limiting, and ephemeral workflow state.
- S3-compatible object storage for attachments and exports.
- External OpenAI or Azure OpenAI model provider.

## Operational Requirements

- Environment-specific secrets management.
- Database migration gate before application rollout.
- Health checks for API, database, Redis, and object storage.
- Structured logs, metrics, tracing, and audit log retention.
- Backups and point-in-time recovery for PostgreSQL.

## Version 1 deployment checks

Before a deployment, run `alembic upgrade head` so the visit follow-up column is present. The `backend` Compose service already executes this migration step before Uvicorn. Keep PostgreSQL and Redis on private networks, inject production secrets through the deployment platform rather than `.env.example`, and set the frontend build argument `VITE_API_BASE_URL` to the public versioned API URL.
