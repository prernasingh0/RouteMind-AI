from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class AIIntent(str, Enum):
    doctor_search = "doctor_search"
    pre_call_planning = "pre_call_planning"
    route_planning = "route_planning"
    post_call_extraction = "post_call_extraction"
    crm_update = "crm_update"
    summary = "summary"
    notification = "notification"
    conversation = "conversation"

class AIRequestContext(BaseModel):
    organization_id: UUID
    user_id: UUID
    conversation_id: UUID | None = None
    trace_id: str

class AIMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AIResponse(BaseModel):
    content: str
    intent: AIIntent
    references: list[str] = []
    tool_calls: list[str] = []
    metadata: dict[str, Any] = {}

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: UUID | None = None
    stream: bool = False

class DoctorSearchAIRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)

class PreCallRequest(BaseModel):
    doctor_id: UUID
    objective: str | None = None

class PostCallRequest(BaseModel):
    doctor_id: UUID
    visit_id: UUID | None = None
    note: str = Field(min_length=1)

class SummaryRequest(BaseModel):
    conversation_id: UUID | None = None
    text: str | None = None

class RouteAIRequest(BaseModel):
    route_id: UUID | None = None
    territory_id: UUID | None = None
    date: datetime | None = None

class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    user_id: UUID
    title: str
    summary: str | None = None
    created_at: datetime
    updated_at: datetime
