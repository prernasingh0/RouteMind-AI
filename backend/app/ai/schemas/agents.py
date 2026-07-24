from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field
from app.ai.schemas.core import AIIntent

class AgentInput(BaseModel):
    prompt: str
    context: dict[str, Any] = {}

class AgentOutput(BaseModel):
    intent: AIIntent
    content: str
    confidence: float = Field(ge=0, le=1)
    references: list[str] = []
    tool_calls: list[str] = []
    structured_data: dict[str, Any] = {}

class PreCallPlan(BaseModel):
    doctor_id: UUID
    objectives: list[str]
    talking_points: list[str]
    possible_objections: list[str]
    suggested_products: list[str]
    risk_alerts: list[str]
    success_probability: float = Field(ge=0, le=1)

class PostCallExtraction(BaseModel):
    products_discussed: list[str]
    samples: list[str]
    doctor_sentiment: str
    competitor_mentions: list[str]
    follow_up: str | None = None
    objections: list[str]
    action_items: list[str]

class RoutePlan(BaseModel):
    route_id: UUID | None = None
    summary: str
    ordered_stops: list[UUID] = []
    risks: list[str] = []
