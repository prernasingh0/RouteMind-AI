# PostgreSQL Schema Design

## Global Conventions

Every table includes:

- `id UUID PRIMARY KEY`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `deleted_at TIMESTAMPTZ NULL`
- Foreign keys with explicit indexes
- Partial indexes that exclude soft-deleted rows where useful

Tenant-owned tables include `organization_id UUID NOT NULL REFERENCES organizations(id)` and an index on `(organization_id, deleted_at)`.

## Core Tables

### organizations
Stores pharmaceutical companies using the platform.

Columns: `id`, `name`, `slug`, `status`, `created_at`, `updated_at`, `deleted_at`.
Indexes: unique active `slug`.

### users
Stores users across organizations.

Columns: `id`, `organization_id`, `email`, `password_hash`, `first_name`, `last_name`, `phone`, `status`, `last_login_at`, timestamps.
Indexes: unique active `(organization_id, email)`, `(organization_id, status)`.

### roles, permissions, role_permissions, user_roles
RBAC model supporting Admin, Manager, Representative and custom tenant roles.

### refresh_tokens
Stores rotated session tokens with revocation metadata.

Columns: `id`, `organization_id`, `user_id`, `token_hash`, `expires_at`, `revoked_at`, `replaced_by_token_id`, timestamps.

## Field Operations Tables

### regions, territories
Regions group territories. Territories own doctors, routes, goals, and assignments.

### doctors
Healthcare professional profile.

Columns: `id`, `organization_id`, `territory_id`, `speciality_id`, `npi`, `first_name`, `last_name`, `clinic_name`, `email`, `phone`, `address_line1`, `address_line2`, `city`, `state`, `postal_code`, `country`, `latitude`, `longitude`, `status`, timestamps.
Indexes: `(organization_id, territory_id)`, `(organization_id, speciality_id)`, full-text name/search index, geospatial latitude/longitude index.

### specialities
Medical specialties for doctors.

### products
Pharma products.

Columns: `id`, `organization_id`, `name`, `brand_name`, `therapeutic_area`, `launch_date`, `status`, timestamps.

### product_priorities
Configurable campaign/product priority by territory, speciality, or doctor segment. This table stores product/campaign priority inputs, not doctor priority.

### call_objectives
Visit objectives generated or assigned before calls.

### visits
Represents scheduled, in-progress, completed, cancelled, or missed visits.

Columns include `doctor_id`, `representative_id`, `territory_id`, `scheduled_start_at`, `scheduled_end_at`, `actual_start_at`, `actual_end_at`, `status`, `channel`, `outcome`.
Indexes: `(organization_id, representative_id, scheduled_start_at)`, `(organization_id, doctor_id, scheduled_start_at)`.

### visit_notes
Structured notes captured manually or extracted by AI.

### interactions
Timeline events across visits, calls, emails, samples, chats, and follow-ups.

### recommendations
AI or manager generated recommendations with source, confidence, rationale, and expiration.

### notifications
User notifications for reminders, tasks, manager announcements, and AI alerts.

## AI and Conversation Tables

### conversations, conversation_messages
Stores live AI chat and visit-related conversations with metadata, tool-call references, citations, and markdown content.

### ai_sessions
Tracks model provider, model name, workflow, token usage, latency, status, and user/session association.

### ai_memories
Long-lived scoped memory for representatives, doctors, territories, and organizations.

### prompt_templates
Versioned prompt templates by workflow and organization.

### model_configurations
Organization-specific model provider, deployment, temperature, output schema, and safety settings.

## Routing and Calendar Tables

### routes, route_stops
Optimized route plans and ordered doctor stops with travel estimates, availability windows, and optimization metadata.

### calendars
Representative working hours, availability, PTO, lunch breaks, and blocked times.

## Analytics and Governance Tables

### activities
Task and activity stream records.

### attachments
S3 object metadata linked to visits, doctors, notes, and messages.

### audit_logs
Immutable audit records for security, compliance, and debugging.

### settings
Hierarchical organization/user settings including priority scoring rules and notification preferences.
