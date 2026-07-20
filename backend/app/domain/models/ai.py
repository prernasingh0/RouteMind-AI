from uuid import UUID
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.base import BaseModel
from app.infrastructure.database.types import JSONDict

class AIConversation(BaseModel):
    __tablename__ = "ai_conversations"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="Conversation")
    summary: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONDict(), nullable=False, default=dict)

class AIConversationMessage(BaseModel):
    __tablename__ = "ai_conversation_messages"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONDict(), nullable=False, default=dict)

class AIMemory(BaseModel):
    __tablename__ = "ai_memories"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id: Mapped[UUID | None] = mapped_column(ForeignKey("ai_conversations.id", ondelete="CASCADE"), index=True)
    memory_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

class AIExecutionLog(BaseModel):
    __tablename__ = "ai_execution_logs"
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    trace_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    graph_node: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    latency_ms: Mapped[int] = mapped_column(nullable=False, default=0)
    prompt_tokens: Mapped[int] = mapped_column(nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(nullable=False, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONDict(), nullable=False, default=dict)
