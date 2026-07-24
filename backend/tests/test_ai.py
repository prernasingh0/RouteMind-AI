from uuid import uuid4
import pytest
from app.ai.graphs.routemind_graph import RouteMindGraph
from app.ai.models.providers import LLMProviderFactory
from app.ai.parsers.structured import StructuredOutputValidator
from app.ai.schemas.agents import AgentOutput
from app.ai.schemas.core import AIIntent
from app.ai.services.orchestrator import AIOrchestratorService

class MockProvider:
    async def generate_structured(self, prompt, output_schema):
        return output_schema(intent=AIIntent.doctor_search if "doctor" in prompt.lower() else AIIntent.conversation, content="structured response", confidence=0.9, references=["crm"], tool_calls=[])
    async def stream_text(self, prompt):
        for token in ["structured", " ", "response"]: yield token

@pytest.mark.asyncio
async def test_graph_routes_doctor_intent():
    graph = RouteMindGraph(MockProvider())
    state = await graph.ainvoke({"message":"Find doctor Smith"})
    assert state["intent"] == AIIntent.doctor_search
    assert state["response"].content == "structured response"

def test_provider_selection_rejects_unknown():
    with pytest.raises(ValueError): LLMProviderFactory.create("unknown")

def test_provider_selection_supports_gemini():
    from app.ai.models.providers import GeminiProvider
    with pytest.MonkeyPatch.context() as m:
        m.setenv("GEMINI_API_KEY", "test-key")
        m.setenv("LLM_PROVIDER", "gemini")
        provider = LLMProviderFactory.create("gemini")
        assert isinstance(provider, GeminiProvider)

@pytest.mark.asyncio
async def test_structured_output_validation_retries():
    calls = {"count": 0}
    async def producer():
        calls["count"] += 1
        if calls["count"] == 1: raise ValueError("bad")
        return AgentOutput(intent=AIIntent.conversation, content="ok", confidence=1)
    result = await StructuredOutputValidator().validate_with_retry(producer)
    assert result.content == "ok"
    assert calls["count"] == 2

@pytest.mark.asyncio
async def test_ai_orchestrator_doctor_search_uses_services(session_factory):
    async with session_factory() as session:
        service = AIOrchestratorService(session, provider=MockProvider())
        result = await service.doctor_search(uuid4(), type("Req", (), {"query":"Smith", "limit":5})())
        assert result["results"] == []
