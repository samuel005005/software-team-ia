from dataclasses import dataclass, field
from typing import Any

from agents.agent_registry import AgentRegistry, create_default_registry
from llm.base_provider import LLMProvider
from llm.llm_request import LLMRequest
from parsers.json_content import parse_json_content
from planning.planner_agent import PlannerAgent
from planning.execution_plan import ExecutionPlan
from project_context.project_snapshot import ProjectSnapshot

PROJECT_TYPE_NEW = "new_project"
PROJECT_TYPE_REVIEW = "existing_project_review"
SUPPORTED_PROJECT_TYPES = {PROJECT_TYPE_NEW, PROJECT_TYPE_REVIEW}

TEMPERATURE = 0.2
MAX_TOKENS = 400


@dataclass
class FactoryPlan:
    """Plan de alto nivel para decidir qué equipo ejecutará la factory."""

    objective: str
    project_type: str
    selected_agents: list[str] = field(default_factory=list)
    execution_plan: ExecutionPlan = field(default_factory=ExecutionPlan)
    metadata: dict[str, Any] = field(default_factory=dict)


class FactoryManagerAgent:
    """Coordina la selección de equipo y construye un ExecutionPlan sin ejecutarlo."""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        registry: AgentRegistry | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._registry = registry or create_default_registry()

    def create_factory_plan(
        self,
        objective: str,
        context: ProjectSnapshot | None = None,
    ) -> FactoryPlan:
        objective_text = objective or ""
        available_agents = self._registry.list_ids()
        if not available_agents:
            raise ValueError("No hay agentes registrados en AgentRegistry")

        project_type = self._classify_project_type(objective_text, context)
        execution_plan = PlannerAgent(
            llm_provider=self._llm_provider,
            registry=self._registry,
        ).plan(
            objective=objective_text,
            project_context=context,
        )
        execution_plan.metadata["project_type"] = project_type
        execution_plan.metadata["context_used"] = context is not None
        selected_agents = execution_plan.nodes
        metadata = {
            "objective": objective_text,
            "source": execution_plan.metadata.get("source", "planner_v1"),
            "provider": execution_plan.metadata.get("provider", ""),
            "available_agents": available_agents,
            "project_type": project_type,
            "context_used": context is not None,
            "project_name": context.project_name if context is not None else "",
        }
        return FactoryPlan(
            objective=objective_text,
            project_type=project_type,
            selected_agents=selected_agents,
            execution_plan=execution_plan,
            metadata=metadata,
        )

    def _classify_project_type(
        self,
        objective: str,
        context: ProjectSnapshot | None = None,
    ) -> str:
        if context is not None:
            return PROJECT_TYPE_REVIEW

        if self._llm_provider is None:
            return self._infer_project_type(objective)

        request = self._build_classification_request(objective)
        try:
            response = self._llm_provider.generate(request)
            data = parse_json_content(response.content)
            project_type = data.get("project_type")
            if project_type not in SUPPORTED_PROJECT_TYPES:
                return self._infer_project_type(objective)
            return str(project_type)
        except Exception:
            return self._infer_project_type(objective)

    def _select_agents(self, project_type: str) -> list[str]:
        desired_capabilities = {
            PROJECT_TYPE_NEW: {
                "requirements_analysis",
                "architecture",
                "implementation_planning",
                "quality_validation",
            },
            PROJECT_TYPE_REVIEW: {
                "requirements_analysis",
                "architecture",
                "quality_validation",
            },
        }.get(project_type, set())

        selected: list[str] = []
        for descriptor in self._registry.list_agents():
            descriptor_capabilities = set(descriptor.capabilities)
            if not desired_capabilities or descriptor_capabilities & desired_capabilities:
                selected.append(descriptor.id)

        if selected:
            return selected
        return self._registry.list_ids()

    def _build_classification_request(self, objective: str) -> LLMRequest:
        available_ids = ", ".join(self._registry.list_ids())
        system_prompt = (
            "Eres un Factory Manager que clasifica objetivos de software.\n"
            "Determina el tipo de trabajo del objetivo.\n\n"
            "Tipos permitidos:\n"
            "- new_project\n"
            "- existing_project_review\n\n"
            "Agentes disponibles en el registry:\n"
            f"{available_ids}\n\n"
            "Responde solo JSON válido con este formato:\n"
            '{\n  "project_type": "new_project"\n}'
        )
        user_prompt = f"Clasifica este objetivo:\n{objective or 'Sin objetivo definido'}"
        return LLMRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

    def _infer_project_type(self, objective: str) -> str:
        text = objective.lower()
        review_keywords = (
            "review",
            "revis",
            "auditar",
            "auditoría",
            "analizar código existente",
            "legacy",
            "actualizar proyecto existente",
            "refactor",
        )
        if any(keyword in text for keyword in review_keywords):
            return PROJECT_TYPE_REVIEW
        return PROJECT_TYPE_NEW
