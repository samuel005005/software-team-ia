from agents.agent_registry import AgentRegistry, create_default_registry
from llm.base_provider import LLMProvider
from planning.execution_plan import ExecutionPlan
from prompts import planner_prompt
from parsers import planner_parser


class PlannerAgent:
    """Genera un plan de ejecución a partir del objetivo del proyecto."""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        registry: AgentRegistry | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._registry = registry or create_default_registry()

    def plan(self, objective: str | None = None) -> ExecutionPlan:
        """Devuelve un plan de ejecución, usando LLM si está disponible."""
        objective_text = objective or ""

        if self._llm_provider is not None:
            try:
                return self._plan_with_llm(objective_text)
            except Exception:
                return self._plan_deterministic(
                    objective_text,
                    source="planner_fallback",
                )

        return self._plan_deterministic(objective_text, source="planner_v1")

    def _plan_with_llm(self, objective: str) -> ExecutionPlan:
        request = planner_prompt.build(objective, self._registry)
        response = self._llm_provider.generate(request)
        return planner_parser.parse(
            response,
            registry=self._registry,
            objective=objective,
        )

    def _plan_deterministic(self, objective: str, *, source: str) -> ExecutionPlan:
        execution_plan = ExecutionPlan(
            metadata={"objective": objective, "source": source},
        )

        for descriptor in self._registry.list_agents():
            execution_plan.add_node(descriptor.id)

        return execution_plan
