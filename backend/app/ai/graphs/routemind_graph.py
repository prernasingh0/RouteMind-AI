from typing import Any, TypedDict
from langgraph.graph import END, StateGraph
from app.ai.models.providers import LLMProvider
from app.ai.parsers.structured import StructuredOutputValidator
from app.ai.schemas.agents import AgentInput, AgentOutput
from app.ai.schemas.core import AIIntent

class RouteMindState(TypedDict, total=False):
    message: str
    intent: AIIntent
    selected_tools: list[str]
    memory: list[str]
    response: AgentOutput
    errors: list[str]

class RouteMindGraph:
    def __init__(self, provider: LLMProvider, tools: Any = None):
        self.provider=provider; self.tools=tools; self.validator=StructuredOutputValidator(); self.compiled_graph=self._compile_graph()
    def _compile_graph(self):
        graph = StateGraph(RouteMindState)
        graph.add_node("supervisor", self.supervisor_node); graph.add_node("intent_detection", self.intent_detection_node); graph.add_node("tool_selection", self.tool_selection_node); graph.add_node("memory_retrieval", self.memory_retrieval_node); graph.add_node("response_generation", self.response_generation_node); graph.add_node("structured_output_validation", self.structured_output_validation_node); graph.add_node("conversation_summary", self.conversation_summary_node)
        graph.set_entry_point("supervisor"); graph.add_edge("supervisor", "intent_detection"); graph.add_conditional_edges("intent_detection", lambda state: "tool_selection", {"tool_selection":"tool_selection"}); graph.add_edge("tool_selection", "memory_retrieval"); graph.add_edge("memory_retrieval", "response_generation"); graph.add_edge("response_generation", "structured_output_validation"); graph.add_edge("structured_output_validation", "conversation_summary"); graph.add_edge("conversation_summary", END)
        return graph.compile()
    async def supervisor_node(self, state: RouteMindState) -> RouteMindState:
        state.setdefault("errors", []); return state
    async def intent_detection_node(self, state: RouteMindState) -> RouteMindState:
        text = state.get("message", "").lower()
        if "route" in text: state["intent"] = AIIntent.route_planning
        elif "pre" in text and "call" in text: state["intent"] = AIIntent.pre_call_planning
        elif "post" in text or "extract" in text: state["intent"] = AIIntent.post_call_extraction
        elif "doctor" in text or "hcp" in text: state["intent"] = AIIntent.doctor_search
        elif "summary" in text or "summarize" in text: state["intent"] = AIIntent.summary
        else: state["intent"] = AIIntent.conversation
        return state
    async def tool_selection_node(self, state: RouteMindState) -> RouteMindState:
        mapping = {AIIntent.doctor_search:["doctor_search"], AIIntent.pre_call_planning:["doctor_search","visit_history","product","campaign","priority"], AIIntent.route_planning:["route","calendar","priority"], AIIntent.post_call_extraction:["visit_history","recommendation"], AIIntent.notification:["notification"]}
        state["selected_tools"] = mapping.get(state.get("intent", AIIntent.conversation), [])
        return state
    async def memory_retrieval_node(self, state: RouteMindState) -> RouteMindState:
        state["memory"] = []
        return state
    async def response_generation_node(self, state: RouteMindState) -> RouteMindState:
        prompt = f"Intent: {state.get('intent')}\nTools: {state.get('selected_tools', [])}\nUser: {state.get('message')}"
        async def produce(): return await self.provider.generate_structured(prompt, AgentOutput)
        state["response"] = await self.validator.validate_with_retry(produce)
        return state
    async def structured_output_validation_node(self, state: RouteMindState) -> RouteMindState:
        if "response" not in state: raise ValueError("RouteMindGraph produced no response")
        return state
    async def conversation_summary_node(self, state: RouteMindState) -> RouteMindState:
        return state
    async def ainvoke(self, state: RouteMindState) -> RouteMindState:
        return await self.compiled_graph.ainvoke(state)
    def visualization(self) -> dict[str, list[str]]:
        return {"supervisor":["intent_detection"], "intent_detection":["tool_selection"], "tool_selection":["memory_retrieval"], "memory_retrieval":["response_generation"], "response_generation":["structured_output_validation"], "structured_output_validation":["conversation_summary"], "conversation_summary":["END"]}
