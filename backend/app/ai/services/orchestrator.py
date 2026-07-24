from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.agents.domain_agents import PostCallExtractionAgent, PreCallPlanningAgent, RoutePlanningAgent, SummaryAgent
from app.ai.graphs.routemind_graph import RouteMindGraph
from app.ai.memory.store import ConversationMemoryStore
from app.ai.models.providers import LLMProvider, LLMProviderFactory
from app.ai.prompts.templates import render_prompt
from app.ai.schemas.agents import AgentInput, AgentOutput, PostCallExtraction, PreCallPlan, RoutePlan
from app.ai.schemas.core import AIResponse, ChatRequest, DoctorSearchAIRequest, PostCallRequest, PreCallRequest, RouteAIRequest, SummaryRequest
from app.ai.tools.service_tools import ServiceToolKit
from app.ai.utils.retry import with_exponential_backoff
from app.services.priority import PriorityCalculationEngine
from app.services.operations import VisitManagementService
from app.schemas.operations import VisitNoteRequest

class AIOrchestratorService:
    def __init__(self, session: AsyncSession, provider: LLMProvider | None = None): self.session=session; self.provider=provider or LLMProviderFactory.create()
    async def chat(self, organization_id: UUID, user_id: UUID, payload: ChatRequest) -> AIResponse:
        memory = ConversationMemoryStore(self.session); conversation = await memory.get_or_create_conversation(organization_id, user_id, payload.conversation_id, payload.message[:80] or "Conversation")
        await memory.append_message(organization_id, conversation.id, "user", payload.message)
        graph = RouteMindGraph(self.provider, ServiceToolKit(self.session, organization_id))
        state = await with_exponential_backoff(lambda: graph.ainvoke({"message": payload.message}))
        output: AgentOutput = state["response"]
        await memory.append_message(organization_id, conversation.id, "assistant", output.content)
        return AIResponse(content=output.content, intent=output.intent, references=output.references, tool_calls=output.tool_calls, metadata={"conversation_id": str(conversation.id), "trace_id": str(uuid4())})
    async def stream_chat(self, organization_id: UUID, user_id: UUID, payload: ChatRequest):
        async for token in self.provider.stream_text(payload.message): yield token
    async def doctor_search(self, organization_id: UUID, payload: DoctorSearchAIRequest):
        doctors = await ServiceToolKit(self.session, organization_id).doctor_search(payload.query, payload.limit)
        return {"results": [{"id": str(d.id), "name": f"{d.first_name} {d.last_name}", "npi": d.npi} for d in doctors]}
    async def precall(self, organization_id: UUID, payload: PreCallRequest) -> PreCallPlan:
        priority = await PriorityCalculationEngine().calculate(self.session, organization_id, payload.doctor_id)
        return await PreCallPlanningAgent(self.provider).plan(payload.doctor_id, f"{payload.objective or ''} priority={priority.total_score}")
    async def postcall(self, organization_id: UUID, user_id: UUID, payload: PostCallRequest) -> PostCallExtraction:
        extraction = await PostCallExtractionAgent(self.provider).extract(payload.doctor_id, payload.note)
        if payload.visit_id:
            outcome = extraction.follow_up or payload.note
            await VisitManagementService(self.session).apply_postcall(organization_id, payload.visit_id, outcome, None)
            await VisitManagementService(self.session).add_note(organization_id, payload.visit_id, user_id, VisitNoteRequest(content=payload.note, note_type="post_call"))
        return extraction
    async def summary(self, payload: SummaryRequest) -> AgentOutput:
        return await SummaryAgent(self.provider).run(AgentInput(prompt=render_prompt("summary", text=payload.text or payload.conversation_id or "")))
    async def route(self, payload: RouteAIRequest) -> RoutePlan:
        return await RoutePlanningAgent(self.provider).plan(str(payload.model_dump()))
