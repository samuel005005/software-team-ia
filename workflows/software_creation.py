from agents.analyst_agent import AnalystAgent
from agents.architect_agent import ArchitectAgent
from agents.base_agent import BaseAgent
from agents.developer_agent import DeveloperAgent
from agents.qa_agent import QAAgent
from execution.execution_graph import ExecutionGraph
from execution.execution_node import ExecutionNode
from llm.base_provider import LLMProvider
from llm.llm_config import LLMConfig
from llm.provider_factory import ProviderFactory
from memory.memory_store import MemoryStore
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


def create_software_creation_graph() -> ExecutionGraph:
    """Construye el grafo de ejecución para la creación de software.

    Analyst -> Architect -> Developer -> QA
    """
    llm_provider = create_llm_provider()
    memory_store = create_memory_store()

    analyst = ExecutionNode(
        id="analyst",
        agent=AnalystAgent(llm_provider=llm_provider, memory_store=memory_store),
    )
    architect = ExecutionNode(
        id="architect",
        agent=ArchitectAgent(llm_provider=llm_provider, memory_store=memory_store),
    )
    developer = ExecutionNode(
        id="developer",
        agent=DeveloperAgent(llm_provider=llm_provider, memory_store=memory_store),
    )
    qa = ExecutionNode(
        id="qa",
        agent=QAAgent(llm_provider=llm_provider, memory_store=memory_store),
    )

    graph = ExecutionGraph()
    graph.add_node(analyst)
    graph.add_node(architect)
    graph.add_node(developer)
    graph.add_node(qa)
    graph.set_start(analyst)
    analyst.connect(architect).connect(developer).connect(qa)

    return graph


def get_software_creation_agents() -> list[BaseAgent]:
    """Retorna el flujo de agentes para la creación de software."""
    return create_software_creation_graph().get_agents()
