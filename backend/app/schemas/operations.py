from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, model_validator

class VisitCreateRequest(BaseModel):
    hcp_id: UUID
    scheduled_at: datetime
    outcome: str | None = Field(default=None, max_length=4000)
    follow_up_at: datetime | None = None

class VisitUpdateRequest(BaseModel):
    scheduled_at: datetime | None = None
    status: str | None = Field(default=None, pattern="^(scheduled|completed|cancelled|missed)$")
    outcome: str | None = Field(default=None, max_length=4000)
    follow_up_at: datetime | None = None

class VisitNoteRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    note_type: str = Field(default="text", max_length=40)

class VisitAttachmentRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=120)
    storage_key: str = Field(min_length=1, max_length=500)
    size_bytes: int = Field(gt=0)

class RouteStopRequest(BaseModel):
    hcp_id: UUID
    planned_arrival_at: datetime | None = None
    planned_departure_at: datetime | None = None

class RouteCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    route_date: date
    stops: list[RouteStopRequest] = Field(default_factory=list)

class RoutePlanRequest(BaseModel):
    route_date: date
    hcp_ids: list[UUID] = Field(default_factory=list)
    workday_start: datetime
    workday_end: datetime
    origin_latitude: float | None = None
    origin_longitude: float | None = None

    @model_validator(mode="after")
    def validate_workday(self):
        if self.workday_end <= self.workday_start:
            raise ValueError("workday_end must be after workday_start")
        return self

class RouteUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    route_date: date | None = None
    status: str | None = Field(default=None, pattern="^(draft|optimized|published|completed)$")

class CalendarRangeRequest(BaseModel):
    starts_at: datetime
    ends_at: datetime

    @model_validator(mode="after")
    def validate_range(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self
