from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.business import HCPCreate, HCPRead, HCPUpdate, PriorityBreakdown

class DoctorSearchParams(BaseModel):
    limit: int = Field(default=25, ge=1, le=200); offset: int = Field(default=0, ge=0); sort: str = "last_name"; search: str | None = None; territory_id: UUID | None = None; region_id: UUID | None = None; specialty_id: UUID | None = None; status: str | None = None; tag: str | None = None
class BulkDoctorOperation(BaseModel): doctor_ids: list[UUID]; operation: str; value: str | UUID | None = None
class DoctorTagCreate(BaseModel): name: str; color: str | None = None
class DoctorPrioritySimulation(BaseModel): days_since_last_visit: int | None = None; visit_frequency_30d: int | None = None; campaign_weight: float | None = None; product_priority: float | None = None; missed_visits: int | None = None; manager_adjustment: float | None = None; territory_target_gap: float | None = None
class TimelineItem(BaseModel): id: UUID; type: str; occurred_at: datetime; title: str; description: str; metadata: dict[str, Any] = {}
class DoctorProfile(BaseModel): doctor: HCPRead; territory: dict[str, Any] | None = None; region: dict[str, Any] | None = None; products: list[dict[str, Any]] = []; visit_history: list[dict[str, Any]] = []; campaigns: list[dict[str, Any]] = []; recommendations: list[dict[str, Any]] = []; current_priority: PriorityBreakdown; recent_ai_interactions: list[dict[str, Any]] = []; tags: list[str] = []
class PriorityHistoryItem(BaseModel): id: UUID; total_score: float; classification: str; factors: dict[str, Any]; explanation: str; created_at: datetime
