from llm.base_provider import LLMProvider
from planning.execution_plan import ExecutionPlan
from prompts import planner_prompt
from parsers import planner_parser


class PlannerAgent:
    """Genera un plan de ejecución a partir del objetivo del proyecto."""

    DEFAULT_FLOW = ("analyst", "architect", "developer", "qa")

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self._llm_provider = llm_provider

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
        request = planner_prompt.build(objective)
        response = self._llm_provider.generate(request)
        return planner_parser.parse(response, objective=objective)

    def _plan_deterministic(self, objective: str, *, source: str) -> ExecutionPlan:
        execution_plan = ExecutionPlan(
            metadata={"objective": objective, "source": source},
        )

        for node_name in self.DEFAULT_FLOW:
            execution_plan.add_node(node_name)

        return execution_plan
