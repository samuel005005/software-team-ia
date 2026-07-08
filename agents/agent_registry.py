from collections.abc import Callable
from dataclasses import dataclass, field

from agents.analyst_agent import AnalystAgent
from agents.architect_agent import ArchitectAgent
from agents.base_agent import BaseAgent
from agents.developer_agent import DeveloperAgent
from agents.qa_agent import QAAgent
from llm.base_provider import LLMProvider
from memory.memory_store import MemoryStore

AgentFactory = Callable[[LLMProvider, MemoryStore], BaseAgent]


@dataclass
class AgentDescriptor:
    """Metadatos y factory de un agente registrado."""

    id: str
    display_name: str
    description: str
    factory: AgentFactory = field(repr=False)
    capabilities: list[str] = field(default_factory=list)


class AgentRegistry:
    """Registro centralizado de agentes disponibles en el harness."""

    def __init__(self) -> None:
        self._descriptors: dict[str, AgentDescriptor] = {}
        self._registration_order: list[str] = []

    def register(self, descriptor: AgentDescriptor) -> None:
        if descriptor.id in self._descriptors:
            raise ValueError(f"Ya existe un agente registrado con id '{descriptor.id}'")

        self._descriptors[descriptor.id] = descriptor
        self._registration_order.append(descriptor.id)

    def get(self, agent_id: str) -> AgentDescriptor | None:
        return self._descriptors.get(agent_id)

    def list_agents(self) -> list[AgentDescriptor]:
        return [self._descriptors[agent_id] for agent_id in self._registration_order]

    def list_capabilities(self) -> dict[str, list[str]]:
        return {
            descriptor.id: list(descriptor.capabilities)
            for descriptor in self.list_agents()
        }

    def list_ids(self) -> list[str]:
        return list(self._registration_order)

    def create_agent(
        self,
        agent_id: str,
        llm_provider: LLMProvider,
        memory_store: MemoryStore,
    ) -> BaseAgent:
        descriptor = self.get(agent_id)
        if descriptor is None:
            raise KeyError(f"No hay agente registrado con id '{agent_id}'")
        return descriptor.factory(llm_provider, memory_store)

    def build_agents(
        self,
        llm_provider: LLMProvider,
        memory_store: MemoryStore,
    ) -> dict[str, BaseAgent]:
        return {
            agent_id: self.create_agent(agent_id, llm_provider, memory_store)
            for agent_id in self._registration_order
        }


def create_default_registry() -> AgentRegistry:
    """Construye el registro por defecto del flujo de creación de software."""
    registry = AgentRegistry()
    registry.register(
        AgentDescriptor(
            id="analyst",
            display_name="Business Analyst",
            description="Genera historias de usuario a partir del objetivo del proyecto",
            capabilities=["user_stories", "requirements_analysis"],
            factory=lambda llm, memory: AnalystAgent(
                llm_provider=llm,
                memory_store=memory,
            ),
        )
    )
    registry.register(
        AgentDescriptor(
            id="architect",
            display_name="Software Architect",
            description="Genera el Software Design Document y la arquitectura",
            capabilities=["architecture", "software_design_document"],
            factory=lambda llm, memory: ArchitectAgent(
                llm_provider=llm,
                memory_store=memory,
            ),
        )
    )
    registry.register(
        AgentDescriptor(
            id="developer",
            display_name="Flutter Developer",
            description="Genera tareas de desarrollo y acciones ejecutables",
            capabilities=["tasks", "actions", "implementation_planning"],
            factory=lambda llm, memory: DeveloperAgent(
                llm_provider=llm,
                memory_store=memory,
            ),
        )
    )
    registry.register(
        AgentDescriptor(
            id="qa",
            display_name="QA Engineer",
            description="Valida la calidad y completitud del proyecto",
            capabilities=["qa_report", "quality_validation"],
            factory=lambda llm, memory: QAAgent(
                llm_provider=llm,
                memory_store=memory,
            ),
        )
    )
    return registry
