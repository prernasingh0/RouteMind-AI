from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.memory.store import ConversationMemoryStore
from app.ai.schemas.core import ChatRequest, ConversationRead, DoctorSearchAIRequest, PostCallRequest, PreCallRequest, RouteAIRequest, SummaryRequest
from app.ai.services.orchestrator import AIOrchestratorService
from app.api.dependencies import get_current_user, require_permissions
from app.infrastructure.database.session import get_session
from app.schemas.auth import UserMe

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/chat")
async def chat(payload: ChatRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("ai:use"))):
    service = AIOrchestratorService(session)
    if payload.stream:
        return StreamingResponse(service.stream_chat(user.organization_id, user.id, payload), media_type="text/event-stream")
    return await service.chat(user.organization_id, user.id, payload)

@router.post("/precall")
async def precall(payload: PreCallRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("ai:use"))): return await AIOrchestratorService(session).precall(user.organization_id, payload)
@router.post("/postcall")
async def postcall(payload: PostCallRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("ai:use"))): return await AIOrchestratorService(session).postcall(user.organization_id, user.id, payload)
@router.post("/summary")
async def summary(payload: SummaryRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("ai:use"))): return await AIOrchestratorService(session).summary(payload)
@router.post("/route")
async def route(payload: RouteAIRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("ai:use"))): return await AIOrchestratorService(session).route(payload)
@router.post("/doctor-search")
async def doctor_search(payload: DoctorSearchAIRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("ai:use"))): return await AIOrchestratorService(session).doctor_search(user.organization_id, payload)

@router.get("/conversations", response_model=list[ConversationRead])
async def conversations(session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("ai:use"))): return await ConversationMemoryStore(session).list_conversations(user.organization_id, user.id)
@router.get("/conversations/{conversation_id}")
async def conversation(conversation_id: UUID, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("ai:use"))): return await ConversationMemoryStore(session).history(user.organization_id, conversation_id)
@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: UUID, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("ai:use"))): await ConversationMemoryStore(session).delete_conversation(user.organization_id, user.id, conversation_id)
