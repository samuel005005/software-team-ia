from agents.agent_registry import AgentRegistry, create_default_registry
from llm.base_provider import LLMProvider
from planning.execution_plan import ExecutionPlan
from prompts import planner_prompt
from parsers import planner_parser
from project_context.project_snapshot import ProjectSnapshot


class PlannerAgent:
    """Genera un plan de ejecución a partir del objetivo del proyecto."""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        registry: AgentRegistry | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._registry = registry or create_default_registry()

    def plan(
        self,
        objective: str | None = None,
        project_context: ProjectSnapshot | None = None,
    ) -> ExecutionPlan:
        """Devuelve un plan de ejecución, usando LLM si está disponible."""
        objective_text = objective or ""

        if self._llm_provider is not None:
            try:
                return self._plan_with_llm(objective_text, project_context)
            except Exception:
                return self._plan_deterministic(
                    objective_text,
                    source="planner_fallback",
                    project_context=project_context,
                )

        return self._plan_deterministic(
            objective_text,
            source="planner_v1",
            project_context=project_context,
        )

    def _plan_with_llm(
        self,
        objective: str,
        project_context: ProjectSnapshot | None,
    ) -> ExecutionPlan:
        request = planner_prompt.build(
            objective,
            self._registry,
            project_context=project_context,
        )
        response = self._llm_provider.generate(request)
        return planner_parser.parse(
            response,
            registry=self._registry,
            objective=objective,
        )

    def _plan_deterministic(
        self,
        objective: str,
        *,
        source: str,
        project_context: ProjectSnapshot | None,
    ) -> ExecutionPlan:
        execution_plan = ExecutionPlan(
            metadata={
                "objective": objective,
                "source": source,
                "context_used": project_context is not None,
                "project_name": (
                    project_context.project_name if project_context is not None else ""
                ),
            },
        )

        for descriptor in self._registry.list_agents():
            execution_plan.add_node(descriptor.id)

        return execution_plan
