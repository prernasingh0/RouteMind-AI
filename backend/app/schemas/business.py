from datetime import date, datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class ListParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
    sort: str = "created_at"
    search: str | None = None

class TenantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

class TenantUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

class RegionCreate(TenantCreate): name: str; code: str | None = None
class RegionUpdate(TenantUpdate): name: str | None = None; code: str | None = None
class RegionRead(BusinessResponse): name: str; code: str | None = None

class TerritoryCreate(TenantCreate): region_id: UUID | None = None; name: str; code: str | None = None; target_visits_per_month: int = Field(default=20, ge=0)
class TerritoryUpdate(TenantUpdate): region_id: UUID | None = None; name: str | None = None; code: str | None = None; target_visits_per_month: int | None = Field(default=None, ge=0)
class TerritoryRead(BusinessResponse): region_id: UUID | None = None; name: str; code: str | None = None; target_visits_per_month: int

class SpecialtyCreate(TenantCreate): name: str
class SpecialtyUpdate(TenantUpdate): name: str | None = None
class SpecialtyRead(BusinessResponse): name: str

class HCPCreate(TenantCreate): territory_id: UUID; specialty_id: UUID | None = None; first_name: str; last_name: str; npi: str | None = None; email: str | None = None; phone: str | None = None; status: str = "active"; engagement_score: float = 0; prescription_trend: float = 0; manager_adjustment: float = 0
class HCPUpdate(TenantUpdate): territory_id: UUID | None = None; specialty_id: UUID | None = None; first_name: str | None = None; last_name: str | None = None; npi: str | None = None; email: str | None = None; phone: str | None = None; status: str | None = None; engagement_score: float | None = None; prescription_trend: float | None = None; manager_adjustment: float | None = None
class HCPRead(BusinessResponse): territory_id: UUID; specialty_id: UUID | None = None; first_name: str; last_name: str; npi: str | None = None; email: str | None = None; phone: str | None = None; status: str = "active"; engagement_score: float; prescription_trend: float; manager_adjustment: float

class AddressCreate(TenantCreate): hcp_id: UUID | None = None; line1: str; line2: str | None = None; city: str; state: str; postal_code: str; country: str = "US"; latitude: float | None = None; longitude: float | None = None
class AddressUpdate(TenantUpdate): hcp_id: UUID | None = None; line1: str | None = None; line2: str | None = None; city: str | None = None; state: str | None = None; postal_code: str | None = None; country: str | None = None; latitude: float | None = None; longitude: float | None = None
class AddressRead(BusinessResponse): hcp_id: UUID | None = None; line1: str; line2: str | None = None; city: str; state: str; postal_code: str; country: str; latitude: float | None = None; longitude: float | None = None

class ProductCategoryCreate(TenantCreate): name: str
class ProductCategoryUpdate(TenantUpdate): name: str | None = None
class ProductCategoryRead(BusinessResponse): name: str
class ProductCreate(TenantCreate): category_id: UUID | None = None; name: str; sku: str | None = None; is_active: bool = True; priority_weight: float = 1.0
class ProductUpdate(TenantUpdate): category_id: UUID | None = None; name: str | None = None; sku: str | None = None; is_active: bool | None = None; priority_weight: float | None = None
class ProductRead(BusinessResponse): category_id: UUID | None = None; name: str; sku: str | None = None; is_active: bool; priority_weight: float
class ProductPriorityRuleCreate(TenantCreate): product_id: UUID; territory_id: UUID | None = None; weight: float = 1.0; criteria: dict[str, Any] = {}
class ProductPriorityRuleUpdate(TenantUpdate): product_id: UUID | None = None; territory_id: UUID | None = None; weight: float | None = None; criteria: dict[str, Any] | None = None
class ProductPriorityRuleRead(BusinessResponse): product_id: UUID; territory_id: UUID | None = None; weight: float; criteria: dict[str, Any]

class CampaignCreate(TenantCreate): product_id: UUID | None = None; name: str; starts_on: date | None = None; ends_on: date | None = None; weight: float = 1.0; is_active: bool = True
class CampaignUpdate(TenantUpdate): product_id: UUID | None = None; name: str | None = None; starts_on: date | None = None; ends_on: date | None = None; weight: float | None = None; is_active: bool | None = None
class CampaignRead(BusinessResponse): product_id: UUID | None = None; name: str; starts_on: date | None = None; ends_on: date | None = None; weight: float; is_active: bool

class VisitCreate(TenantCreate): hcp_id: UUID; user_id: UUID; scheduled_at: datetime; completed_at: datetime | None = None; status: str = "scheduled"; outcome: str | None = None
class VisitUpdate(TenantUpdate): hcp_id: UUID | None = None; user_id: UUID | None = None; scheduled_at: datetime | None = None; completed_at: datetime | None = None; status: str | None = None; outcome: str | None = None
class VisitRead(BusinessResponse): hcp_id: UUID; user_id: UUID; scheduled_at: datetime; completed_at: datetime | None = None; status: str; outcome: str | None = None; follow_up_at: datetime | None = None
class VisitNoteCreate(TenantCreate): visit_id: UUID; author_user_id: UUID; note_type: str = "text"; content: str
class VisitNoteUpdate(TenantUpdate): visit_id: UUID | None = None; author_user_id: UUID | None = None; note_type: str | None = None; content: str | None = None
class VisitNoteRead(BusinessResponse): visit_id: UUID; author_user_id: UUID; note_type: str; content: str

class CallObjectiveCreate(TenantCreate): hcp_id: UUID; product_id: UUID | None = None; title: str; status: str = "open"; due_at: datetime | None = None
class CallObjectiveUpdate(TenantUpdate): hcp_id: UUID | None = None; product_id: UUID | None = None; title: str | None = None; status: str | None = None; due_at: datetime | None = None
class CallObjectiveRead(BusinessResponse): hcp_id: UUID; product_id: UUID | None = None; title: str; status: str; due_at: datetime | None = None
class RecommendationCreate(TenantCreate): hcp_id: UUID; product_id: UUID | None = None; title: str; rationale: str; score: float = 0; status: str = "active"
class RecommendationUpdate(TenantUpdate): hcp_id: UUID | None = None; product_id: UUID | None = None; title: str | None = None; rationale: str | None = None; score: float | None = None; status: str | None = None
class RecommendationRead(BusinessResponse): hcp_id: UUID; product_id: UUID | None = None; title: str; rationale: str; score: float; status: str
class InteractionCreate(TenantCreate): hcp_id: UUID; user_id: UUID; channel: str; occurred_at: datetime; summary: str; sentiment: str | None = None
class InteractionUpdate(TenantUpdate): hcp_id: UUID | None = None; user_id: UUID | None = None; channel: str | None = None; occurred_at: datetime | None = None; summary: str | None = None; sentiment: str | None = None
class InteractionRead(BusinessResponse): hcp_id: UUID; user_id: UUID; channel: str; occurred_at: datetime; summary: str; sentiment: str | None = None

class RouteCreate(TenantCreate): user_id: UUID; name: str; route_date: date; status: str = "draft"
class RouteUpdate(TenantUpdate): user_id: UUID | None = None; name: str | None = None; route_date: date | None = None; status: str | None = None
class RouteRead(BusinessResponse): user_id: UUID; name: str; route_date: date; status: str
class RouteStopCreate(TenantCreate): route_id: UUID; hcp_id: UUID; sequence: int; planned_arrival_at: datetime | None = None; planned_departure_at: datetime | None = None; travel_minutes: int | None = None
class RouteStopUpdate(TenantUpdate): route_id: UUID | None = None; hcp_id: UUID | None = None; sequence: int | None = None; planned_arrival_at: datetime | None = None; planned_departure_at: datetime | None = None; travel_minutes: int | None = None
class RouteStopRead(BusinessResponse): route_id: UUID; hcp_id: UUID; sequence: int; planned_arrival_at: datetime | None = None; planned_departure_at: datetime | None = None; travel_minutes: int | None = None

class CalendarEventCreate(TenantCreate): user_id: UUID; hcp_id: UUID | None = None; title: str; starts_at: datetime; ends_at: datetime; event_type: str = "visit"
class CalendarEventUpdate(TenantUpdate): user_id: UUID | None = None; hcp_id: UUID | None = None; title: str | None = None; starts_at: datetime | None = None; ends_at: datetime | None = None; event_type: str | None = None
class CalendarEventRead(BusinessResponse): user_id: UUID; hcp_id: UUID | None = None; title: str; starts_at: datetime; ends_at: datetime; event_type: str
class ActivityCreate(TenantCreate): user_id: UUID | None = None; entity_type: str; entity_id: UUID | None = None; action: str; description: str
class ActivityUpdate(TenantUpdate): user_id: UUID | None = None; entity_type: str | None = None; entity_id: UUID | None = None; action: str | None = None; description: str | None = None
class ActivityRead(BusinessResponse): user_id: UUID | None = None; entity_type: str; entity_id: UUID | None = None; action: str; description: str
class AttachmentCreate(TenantCreate): uploaded_by_user_id: UUID; entity_type: str; entity_id: UUID | None = None; file_name: str; content_type: str; storage_key: str; size_bytes: int
class AttachmentUpdate(TenantUpdate): uploaded_by_user_id: UUID | None = None; entity_type: str | None = None; entity_id: UUID | None = None; file_name: str | None = None; content_type: str | None = None; storage_key: str | None = None; size_bytes: int | None = None
class AttachmentRead(BusinessResponse): uploaded_by_user_id: UUID; entity_type: str; entity_id: UUID | None = None; file_name: str; content_type: str; storage_key: str; size_bytes: int
class NotificationCreate(TenantCreate): user_id: UUID; title: str; body: str; notification_type: str; read_at: datetime | None = None; metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata")
class NotificationUpdate(TenantUpdate): user_id: UUID | None = None; title: str | None = None; body: str | None = None; notification_type: str | None = None; read_at: datetime | None = None; metadata_: dict[str, Any] | None = Field(default=None, alias="metadata")
class NotificationRead(BusinessResponse): user_id: UUID; title: str; body: str; notification_type: str; read_at: datetime | None = None; metadata_: dict[str, Any] = Field(alias="metadata")
class SettingsCreate(TenantCreate): scope: str; key: str; value: dict[str, Any]
class SettingsUpdate(TenantUpdate): scope: str | None = None; key: str | None = None; value: dict[str, Any] | None = None
class SettingsRead(BusinessResponse): scope: str; key: str; value: dict[str, Any]

class PriorityBreakdown(BaseModel):
    hcp_id: UUID
    total_score: float
    classification: str
    factors: dict[str, float]
