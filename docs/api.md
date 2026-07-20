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
