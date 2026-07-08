from agents.agent_registry import AgentRegistry, create_default_registry
from agents.base_agent import BaseAgent
from execution.execution_graph import ExecutionGraph
from execution.execution_node import ExecutionNode
from llm.base_provider import LLMProvider
from llm.llm_config import LLMConfig
from llm.provider_factory import ProviderFactory
from memory.memory_store import MemoryStore
from planning.execution_plan import ExecutionPlan
from planning.planner_agent import PlannerAgent
from tools.filesystem_tool import FileSystemTool
from tools.terminal_tool import TerminalTool
from tools.tool_executor import ToolExecutor


def create_tool_executor() -> ToolExecutor:
    executor = ToolExecutor()
    executor.register(FileSystemTool())
    executor.register(TerminalTool())
    return executor


def create_llm_provider() -> LLMProvider:
    return ProviderFactory.from_config(LLMConfig.from_env())


def create_memory_store() -> MemoryStore:
    return MemoryStore()


def build_graph_from_plan(
    plan: ExecutionPlan,
    agents: dict[str, BaseAgent],
) -> ExecutionGraph:
    """Construye un ExecutionGraph lineal a partir de un ExecutionPlan."""
    graph = ExecutionGraph()
    nodes: list[ExecutionNode] = []

    for node_id in plan.nodes:
        agent = agents.get(node_id)
        if agent is None:
            raise ValueError(f"No hay agente registrado para el nodo '{node_id}'")

        node = ExecutionNode(id=node_id, agent=agent)
        graph.add_node(node)
        nodes.append(node)

    if not nodes:
        return graph

    graph.set_start(nodes[0])
    for index in range(len(nodes) - 1):
        nodes[index].connect(nodes[index + 1])

    return graph


def create_software_creation_plan(objective: str | None = None) -> ExecutionPlan:
    llm_provider = create_llm_provider()
    registry = create_default_registry()
    return PlannerAgent(llm_provider=llm_provider, registry=registry).plan(objective)


def create_software_creation_graph() -> ExecutionGraph:
    """Construye el grafo de ejecución para la creación de software."""
    llm_provider = create_llm_provider()
    memory_store = create_memory_store()
    registry = create_default_registry()
    plan = PlannerAgent(llm_provider=llm_provider, registry=registry).plan()
    agents = registry.build_agents(llm_provider, memory_store)
    return build_graph_from_plan(plan, agents)


def get_software_creation_agents() -> list[BaseAgent]:
    """Retorna el flujo de agentes para la creación de software."""
    return create_software_creation_graph().get_agents()
