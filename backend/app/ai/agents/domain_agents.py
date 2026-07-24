from app.ai.agents.base import BaseAgent
from app.ai.prompts.templates import render_prompt
from app.ai.schemas.agents import AgentInput, AgentOutput, PostCallExtraction, PreCallPlan, RoutePlan
from app.ai.schemas.core import AIIntent

class DoctorSearchAgent(BaseAgent):
    intent=AIIntent.doctor_search
    async def search(self, query: str) -> AgentOutput:
        return await self.run(AgentInput(prompt=render_prompt("doctor_search", query=query), context={"tool":"doctor_search"}))
class PreCallPlanningAgent(BaseAgent):
    intent=AIIntent.pre_call_planning
    async def plan(self, doctor_id, objective=None) -> PreCallPlan:
        return await self.provider.generate_structured(render_prompt("pre_call", doctor_id=doctor_id, objective=objective or ""), PreCallPlan)
class RoutePlanningAgent(BaseAgent):
    intent=AIIntent.route_planning
    async def plan(self, context: str) -> RoutePlan:
        return await self.provider.generate_structured(render_prompt("route", context=context), RoutePlan)
class PostCallExtractionAgent(BaseAgent):
    intent=AIIntent.post_call_extraction
    async def extract(self, doctor_id, note: str) -> PostCallExtraction:
        return await self.provider.generate_structured(render_prompt("post_call", doctor_id=doctor_id, note=note), PostCallExtraction)
class ConversationAgent(BaseAgent):
    intent=AIIntent.conversation
    async def respond(self, message: str) -> AgentOutput:
        return await self.run(AgentInput(prompt=message, context={"tool":"conversation"}))
class CRMAgent(BaseAgent):
    intent=AIIntent.crm_update
    async def update(self, instruction: str) -> AgentOutput:
        return await self.run(AgentInput(prompt=instruction, context={"tool":"crm_update"}))
class MemoryAgent(BaseAgent):
    intent=AIIntent.conversation
    async def remember(self, content: str) -> AgentOutput:
        return await self.run(AgentInput(prompt=f"Store useful memory: {content}", context={"tool":"memory"}))
class SummaryAgent(BaseAgent):
    intent=AIIntent.summary
class NotificationAgent(BaseAgent):
    intent=AIIntent.notification
    async def notify(self, content: str) -> AgentOutput:
        return await self.run(AgentInput(prompt=content, context={"tool":"notification"}))
