from unittest.mock import MagicMock

from llm.claude_provider import ClaudeProvider
from llm.gemini_provider import GeminiProvider
from llm.llm_request import LLMRequest
from llm.mock_provider import MockLLMProvider
from llm.openai_provider import OpenAIProvider
from memory.memory_store import MemoryStore
from orchestrator.orchestrator import Orchestrator
from planning.planner_agent import PlannerAgent
from state.project_state import ProjectState
from workspace.workspace import Workspace
from workflows.software_creation import (
    build_agents_for_software_creation,
    build_graph_from_plan,
    create_tool_executor,
)


def build_mock_content(request: LLMRequest) -> str:
    """Reutiliza las respuestas estructuradas del mock sin llamadas HTTP reales."""
    return MockLLMProvider()._build_content(request)


def build_openai_provider_with_router() -> tuple[OpenAIProvider, MagicMock]:
    client = MagicMock()
    provider = OpenAIProvider(api_key="test-api-key", model="gpt-4o", client=client)

    def create(**kwargs):
        messages = kwargs["messages"]
        request = LLMRequest(
            system_prompt=messages[0]["content"],
            user_prompt=messages[1]["content"],
            temperature=kwargs.get("temperature", 0.0),
            max_tokens=kwargs.get("max_tokens"),
            model=kwargs.get("model"),
        )
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = build_mock_content(request)
        response.choices[0].finish_reason = "stop"
        response.usage.prompt_tokens = 10
        response.usage.completion_tokens = 10
        return response

    client.chat.completions.create.side_effect = create
    return provider, client


def build_claude_provider_with_router() -> tuple[ClaudeProvider, MagicMock]:
    client = MagicMock()
    provider = ClaudeProvider(
        api_key="test-api-key",
        model="claude-3-5-sonnet-latest",
        client=client,
    )

    def create(**kwargs):
        request = LLMRequest(
            system_prompt=kwargs["system"],
            user_prompt=kwargs["messages"][0]["content"],
            temperature=kwargs.get("temperature", 0.0),
            max_tokens=kwargs.get("max_tokens"),
            model=kwargs.get("model"),
        )
        text_block = MagicMock()
        text_block.text = build_mock_content(request)
        response = MagicMock()
        response.content = [text_block]
        response.stop_reason = "end_turn"
        response.usage.input_tokens = 10
        response.usage.output_tokens = 10
        return response

    client.messages.create.side_effect = create
    return provider, client


def build_gemini_provider_with_router() -> tuple[GeminiProvider, MagicMock]:
    client = MagicMock()
    provider = GeminiProvider(
        api_key="test-api-key",
        model="gemini-2.0-flash",
        client=client,
    )

    def generate_content(**kwargs):
        config = kwargs.get("config")
        system_prompt = getattr(config, "system_instruction", "") or ""
        request = LLMRequest(
            system_prompt=system_prompt,
            user_prompt=kwargs["contents"],
            temperature=getattr(config, "temperature", 0.0),
            max_tokens=getattr(config, "max_output_tokens", None),
            model=kwargs.get("model"),
        )
        response = MagicMock()
        response.text = build_mock_content(request)
        response.usage_metadata.prompt_token_count = 10
        response.usage_metadata.candidates_token_count = 10
        candidate = MagicMock()
        candidate.finish_reason = "STOP"
        response.candidates = [candidate]
        return response

    client.models.generate_content.side_effect = generate_content
    return provider, client


def run_software_creation_flow(
    llm_provider,
    *,
    workspace_root: str,
    objective: str = "Crear una aplicación móvil para administrar una barbería",
) -> tuple[ProjectState, object, dict[str, object]]:
    from agents.agent_registry import create_default_registry

    memory_store = MemoryStore()
    workspace = Workspace(workspace_root)
    registry = create_default_registry()
    plan = PlannerAgent(llm_provider=llm_provider, registry=registry).plan(objective)
    agents = build_agents_for_software_creation(
        llm_provider,
        memory_store,
        workspace,
    )
    graph = build_graph_from_plan(plan, agents)
    orchestrator = Orchestrator(
        graph.get_agents(),
        tool_executor=create_tool_executor(),
    )
    state = ProjectState(
        project_name="barberia-app",
        description=objective,
    )
    final_state = orchestrator.run(state)
    return final_state, plan, agents
