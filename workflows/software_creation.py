from agents.analyst_agent import AnalystAgent
from agents.architect_agent import ArchitectAgent
from agents.base_agent import BaseAgent
from agents.developer_agent import DeveloperAgent
from agents.qa_agent import QAAgent
from llm.mock_provider import MockLLMProvider
from memory.memory_store import MemoryStore
from tools.filesystem_tool import FileSystemTool
from tools.terminal_tool import TerminalTool
from tools.tool_executor import ToolExecutor


def create_tool_executor() -> ToolExecutor:
    executor = ToolExecutor()
    executor.register(FileSystemTool())
    executor.register(TerminalTool())
    return executor


def create_llm_provider() -> MockLLMProvider:
    return MockLLMProvider()


def create_memory_store() -> MemoryStore:
    return MemoryStore()


def get_software_creation_agents() -> list[BaseAgent]:
    """Retorna el flujo de agentes para la creación de software.

    AnalystAgent -> ArchitectAgent -> DeveloperAgent -> QAAgent
    """
    llm_provider = create_llm_provider()
    memory_store = create_memory_store()

    return [
        AnalystAgent(llm_provider=llm_provider, memory_store=memory_store),
        ArchitectAgent(llm_provider=llm_provider, memory_store=memory_store),
        DeveloperAgent(),
        QAAgent(),
    ]
