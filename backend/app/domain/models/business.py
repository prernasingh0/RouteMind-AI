from datetime import date, datetime
from uuid import UUID
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.base import BaseModel
from app.infrastructure.database.types import JSONDict

class Region(BaseModel):
    __tablename__ = "regions"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    code: Mapped[str | None] = mapped_column(String(64), index=True)
    territories: Mapped[list["Territory"]] = relationship(back_populates="region")
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_regions_org_name"),)

class Territory(BaseModel):
    __tablename__ = "territories"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    region_id: Mapped[UUID | None] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    code: Mapped[str | None] = mapped_column(String(64), index=True)
    target_visits_per_month: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    region: Mapped[Region | None] = relationship(back_populates="territories")
    doctors: Mapped[list["HCP"]] = relationship(back_populates="territory")

class Specialty(BaseModel):
    __tablename__ = "specialties"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_specialties_org_name"),)

class HCP(BaseModel):
    __tablename__ = "hcps"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id", ondelete="RESTRICT"), nullable=False, index=True)
    specialty_id: Mapped[UUID | None] = mapped_column(ForeignKey("specialties.id", ondelete="SET NULL"), index=True)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    npi: Mapped[str | None] = mapped_column(String(40), index=True)
    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active", index=True)
    engagement_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    prescription_trend: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    manager_adjustment: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    territory: Mapped[Territory] = relationship(back_populates="doctors")
    specialty: Mapped[Specialty | None] = relationship()
    visits: Mapped[list["Visit"]] = relationship(back_populates="doctor")
    addresses: Mapped[list["Address"]] = relationship(back_populates="doctor")

class Address(BaseModel):
    __tablename__ = "addresses"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID | None] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), index=True)
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(80), nullable=False, default="US")
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    doctor: Mapped[HCP | None] = relationship(back_populates="addresses")

class ProductCategory(BaseModel):
    __tablename__ = "product_categories"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)

class Product(BaseModel):
    __tablename__ = "products"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[UUID | None] = mapped_column(ForeignKey("product_categories.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    sku: Mapped[str | None] = mapped_column(String(80), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    priority_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

class Campaign(BaseModel):
    __tablename__ = "campaigns"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    starts_on: Mapped[date | None] = mapped_column(Date)
    ends_on: Mapped[date | None] = mapped_column(Date)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

class ProductPriorityRule(BaseModel):
    __tablename__ = "product_priority_rules"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    territory_id: Mapped[UUID | None] = mapped_column(ForeignKey("territories.id", ondelete="CASCADE"), index=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    criteria: Mapped[dict] = mapped_column(JSONDict(), nullable=False, default=dict)

class Visit(BaseModel):
    __tablename__ = "visits"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="scheduled", index=True)
    outcome: Mapped[str | None] = mapped_column(Text)
    follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    doctor: Mapped[HCP] = relationship(back_populates="visits")
    notes: Mapped[list["VisitNote"]] = relationship(back_populates="visit")

class VisitNote(BaseModel):
    __tablename__ = "visit_notes"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    visit_id: Mapped[UUID] = mapped_column(ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, index=True)
    author_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    note_type: Mapped[str] = mapped_column(String(40), nullable=False, default="text")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    visit: Mapped[Visit] = relationship(back_populates="notes")

class CallObjective(BaseModel):
    __tablename__ = "call_objectives"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="open", index=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

class Recommendation(BaseModel):
    __tablename__ = "recommendations"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active", index=True)

class Interaction(BaseModel):
    __tablename__ = "interactions"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[str | None] = mapped_column(String(40), index=True)

class Route(BaseModel):
    __tablename__ = "routes"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    route_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft", index=True)
    stops: Mapped[list["RouteStop"]] = relationship(back_populates="route", order_by="RouteStop.sequence")

class RouteStop(BaseModel):
    __tablename__ = "route_stops"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    route_id: Mapped[UUID] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_departure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    travel_minutes: Mapped[int | None] = mapped_column(Integer)
    route: Mapped[Route] = relationship(back_populates="stops")

class CalendarEvent(BaseModel):
    __tablename__ = "calendar_events"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID | None] = mapped_column(ForeignKey("hcps.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False, default="visit", index=True)

class Activity(BaseModel):
    __tablename__ = "activities"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[UUID | None] = mapped_column(index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

class Attachment(BaseModel):
    __tablename__ = "attachments"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[UUID | None] = mapped_column(index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

class Notification(BaseModel):
    __tablename__ = "notifications"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONDict(), nullable=False, default=dict)

class Settings(BaseModel):
    __tablename__ = "settings"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSONDict(), nullable=False, default=dict)
    __table_args__ = (UniqueConstraint("organization_id", "scope", "key", name="uq_settings_org_scope_key"),)

class DoctorTag(BaseModel):
    __tablename__ = "doctor_tags"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    color: Mapped[str | None] = mapped_column(String(20))
    __table_args__ = (UniqueConstraint("organization_id", "hcp_id", "name", name="uq_doctor_tags_org_hcp_name"),)

class DoctorProductAssociation(BaseModel):
    __tablename__ = "doctor_product_associations"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(60), nullable=False, default="discussed", index=True)
    strength: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    __table_args__ = (UniqueConstraint("organization_id", "hcp_id", "product_id", name="uq_doctor_products_org_hcp_product"),)

class DoctorCampaignAssociation(BaseModel):
    __tablename__ = "doctor_campaign_associations"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(60), nullable=False, default="targeted", index=True)
    __table_args__ = (UniqueConstraint("organization_id", "hcp_id", "campaign_id", name="uq_doctor_campaigns_org_hcp_campaign"),)

class DoctorPrioritySnapshot(BaseModel):
    __tablename__ = "doctor_priority_snapshots"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id: Mapped[UUID] = mapped_column(ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    classification: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    factors: Mapped[dict] = mapped_column(JSONDict(), nullable=False, default=dict)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
