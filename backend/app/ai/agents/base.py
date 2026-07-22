import time
import structlog
from app.ai.models.providers import LLMProvider
from app.ai.schemas.agents import AgentInput, AgentOutput
from app.ai.schemas.core import AIIntent
logger = structlog.get_logger()

class BaseAgent:
    intent: AIIntent = AIIntent.conversation
    def __init__(self, provider: LLMProvider, tools=None): self.provider=provider; self.tools=tools
    async def run(self, payload: AgentInput) -> AgentOutput:
        start = time.perf_counter()
        try:
            result = await self.provider.generate_structured(payload.prompt, AgentOutput)
            logger.info("agent_completed", agent=self.__class__.__name__, latency_ms=round((time.perf_counter()-start)*1000,2))
            return result
        except Exception as exc:
            logger.warning("agent_failed", agent=self.__class__.__name__, error=str(exc))
            raise
