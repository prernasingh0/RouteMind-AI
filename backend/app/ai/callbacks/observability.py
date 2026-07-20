import time
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import AIExecutionLog

class AIExecutionTracer:
    def __init__(self, session: AsyncSession, organization_id: UUID, user_id: UUID, trace_id: str): self.session=session; self.organization_id=organization_id; self.user_id=user_id; self.trace_id=trace_id
    async def record(self, node: str, start: float, status: str = "success", prompt_tokens: int = 0, completion_tokens: int = 0, estimated_cost_usd: float = 0, metadata: dict | None = None):
        log = AIExecutionLog(organization_id=self.organization_id, user_id=self.user_id, trace_id=self.trace_id, graph_node=node, latency_ms=int((time.perf_counter()-start)*1000), prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, estimated_cost_usd=estimated_cost_usd, status=status, metadata_=metadata or {})
        self.session.add(log); await self.session.commit(); return log
