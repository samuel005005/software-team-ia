from typing import Any

from llm.base_provider import LLMProvider
from parsers import reviewer_parser
from prompts import reviewer_prompt
from review.review_result import ReviewResult


class ReviewerAgent:
    """Revisa la salida de otros agentes sin modificar el flujo de ejecución."""

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self._llm_provider = llm_provider

    def review(
        self,
        *,
        reviewed_agent: str,
        objective: str = "",
        agent_output: Any,
        review_criteria: list[str] | None = None,
    ) -> ReviewResult:
        """Evalúa la salida de un agente y devuelve un ReviewResult estructurado."""
        if self._llm_provider is not None:
            try:
                return self._review_with_llm(
                    reviewed_agent=reviewed_agent,
                    objective=objective,
                    agent_output=agent_output,
                    review_criteria=review_criteria,
                )
            except Exception:
                return self._review_fallback(
                    reviewed_agent=reviewed_agent,
                    objective=objective,
                )

        return self._review_deterministic(
            reviewed_agent=reviewed_agent,
            objective=objective,
            agent_output=agent_output,
            source="reviewer_v1",
        )

    def _review_with_llm(
        self,
        *,
        reviewed_agent: str,
        objective: str,
        agent_output: Any,
        review_criteria: list[str] | None,
    ) -> ReviewResult:
        request = reviewer_prompt.build(
            reviewed_agent=reviewed_agent,
            objective=objective,
            agent_output=agent_output,
            review_criteria=review_criteria,
        )
        response = self._llm_provider.generate(request)
        return reviewer_parser.parse(
            response,
            reviewed_agent=reviewed_agent,
            objective=objective,
        )

    def _review_deterministic(
        self,
        *,
        reviewed_agent: str,
        objective: str,
        agent_output: Any,
        source: str,
    ) -> ReviewResult:
        has_output = bool(agent_output)

        return ReviewResult(
            reviewed_agent=reviewed_agent,
            approved=has_output,
            score=1.0 if has_output else 0.5,
            summary=f"Revisión determinista para {reviewed_agent}",
            issues=[] if has_output else ["Salida vacía o ausente"],
            recommendations=[],
            metadata={"source": source, "objective": objective},
        )

    def _review_fallback(self, *, reviewed_agent: str, objective: str) -> ReviewResult:
        return ReviewResult(
            reviewed_agent=reviewed_agent,
            approved=True,
            score=1.0,
            summary="Fallback review",
            issues=[],
            recommendations=[],
            metadata={"source": "reviewer_fallback", "objective": objective},
        )
