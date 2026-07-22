from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import AIConversation, AIConversationMessage, AIMemory
from app.infrastructure.cache.redis import get_redis

class ConversationMemoryStore:
    def __init__(self, session: AsyncSession): self.session = session
    async def get_or_create_conversation(self, organization_id: UUID, user_id: UUID, conversation_id: UUID | None, title: str) -> AIConversation:
        if conversation_id:
            conversation = await self.session.scalar(select(AIConversation).where(AIConversation.id==conversation_id, AIConversation.organization_id==organization_id, AIConversation.user_id==user_id, AIConversation.deleted_at.is_(None)))
            if conversation: return conversation
        conversation = AIConversation(organization_id=organization_id, user_id=user_id, title=title)
        self.session.add(conversation); await self.session.commit(); await self.session.refresh(conversation); return conversation
    async def append_message(self, organization_id: UUID, conversation_id: UUID, role: str, content: str) -> AIConversationMessage:
        message = AIConversationMessage(organization_id=organization_id, conversation_id=conversation_id, role=role, content=content, metadata_={})
        self.session.add(message); await self.session.commit(); await self.session.refresh(message)
        redis = await get_redis(); await redis.lpush(f"conversation:{conversation_id}:messages", f"{role}: {content}"); await redis.ltrim(f"conversation:{conversation_id}:messages", 0, 19)
        return message
    async def history(self, organization_id: UUID, conversation_id: UUID, limit: int = 20) -> list[AIConversationMessage]:
        stmt = select(AIConversationMessage).where(AIConversationMessage.organization_id==organization_id, AIConversationMessage.conversation_id==conversation_id, AIConversationMessage.deleted_at.is_(None)).order_by(AIConversationMessage.created_at.desc()).limit(limit)
        return list((await self.session.scalars(stmt)).all())
    async def list_conversations(self, organization_id: UUID, user_id: UUID):
        stmt = select(AIConversation).where(AIConversation.organization_id==organization_id, AIConversation.user_id==user_id, AIConversation.deleted_at.is_(None)).order_by(AIConversation.updated_at.desc())
        return list((await self.session.scalars(stmt)).all())
    async def delete_conversation(self, organization_id: UUID, user_id: UUID, conversation_id: UUID) -> None:
        conversation = await self.session.scalar(select(AIConversation).where(AIConversation.id==conversation_id, AIConversation.organization_id==organization_id, AIConversation.user_id==user_id))
        if conversation: conversation.mark_deleted(); self.session.add(conversation); await self.session.commit()
    async def store_summary(self, organization_id: UUID, user_id: UUID, conversation_id: UUID, summary: str) -> AIMemory:
        memory = AIMemory(organization_id=organization_id, user_id=user_id, conversation_id=conversation_id, memory_type="summary", content=summary)
        self.session.add(memory); await self.session.commit(); await self.session.refresh(memory); return memory
