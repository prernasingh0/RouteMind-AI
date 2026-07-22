# API Design

RouteMind AI exposes versioned REST APIs under `/api/v1`. All endpoints use JSON, Pydantic v2 validation, structured error responses, pagination, filtering, sorting, and OpenAPI documentation.

## Conventions

- Authentication: `Authorization: Bearer <access_token>`.
- Pagination: `page`, `page_size`, `total`, `items`.
- Sorting: `sort=field:asc` or `sort=field:desc`.
- Filtering: explicit query parameters per resource.
- Tenant scope: resolved from authenticated user organization membership.

## Initial Resource Groups

- `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/forgot-password`, `/auth/logout`
- `/dashboard/kpis`, `/dashboard/today`, `/dashboard/recommendations`
- `/doctors`, `/doctors/{doctor_id}`, `/doctors/{doctor_id}/timeline`
- `/visits`, `/visits/{visit_id}`, `/visits/{visit_id}/notes`
- `/planning/pre-call/{doctor_id}`
- `/routes/optimize`, `/routes/{route_id}`
- `/chat/conversations`, `/chat/conversations/{conversation_id}/messages`
- `/insights/products`, `/insights/territories`, `/insights/visits`
- `/notifications`
- `/settings/profile`, `/settings/organization`, `/settings/prompts`, `/settings/models`

## Version 1 field operations

All routes below are tenant-scoped and require an access token with the indicated permission.

| Endpoint | Permission | Purpose |
| --- | --- | --- |
| `POST /api/v1/visits` | `visits:write` | Schedule a visit for the authenticated representative. |
| `PATCH` / `DELETE /api/v1/visits/{id}` | `visits:write` | Reschedule, capture outcome/follow-up, or soft delete a visit. |
| `POST /api/v1/visits/{id}/notes` | `visits:write` | Capture a visit note. |
| `GET /api/v1/visits/{id}/timeline` | `visits:read` | Return the visit, notes, and attachments. |
| `POST /api/v1/routes` | `routes:write` | Create a route and its ordered stops. |
| `POST /api/v1/routes/{id}/optimize` | `routes:write` | Optimize stop ordering and return map-ready coordinates. |
| `GET /api/v1/calendar?starts_at=&ends_at=` | `calendar:read` | Return visits and personal calendar events in a validated range. |

`POST /api/v1/ai/postcall` accepts text or voice-transcript-derived notes. When `visit_id` is supplied, the API persists the original note and marks the visit completed with the extracted follow-up outcome.
