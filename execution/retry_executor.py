from copy import deepcopy
from dataclasses import fields
from typing import Any

from agents.agent_result import AgentResult
from agents.base_agent import BaseAgent
from execution.retry_policy import RetryPolicy
from execution.retry_result import RetryResult
from quality.quality_context import QualityContext
from quality.quality_pipeline import QualityPipeline
from state.project_state import ProjectState


class RetryExecutor:
    """Motor aislado que ejecuta un agente con evaluación de calidad y reintentos."""

    def __init__(
        self,
        quality_pipeline: QualityPipeline | None = None,
        retry_policy: RetryPolicy | None = None,
        max_retries: int = 3,
    ) -> None:
        self._quality_pipeline = quality_pipeline or QualityPipeline()
        self._retry_policy = retry_policy or RetryPolicy(max_retries=max_retries)
        self._max_retries = max_retries

    def execute(self, agent: BaseAgent, *args: Any, **kwargs: Any) -> RetryResult:
        objective = self._extract_objective(*args, **kwargs)
        state = self._find_project_state(*args, **kwargs)
        initial_snapshot = deepcopy(state) if state is not None else None
        success_snapshot: ProjectState | None = None
        history: list[dict[str, Any]] = []
        retry_count = 0
        attempts = 0
        last_valid_result: AgentResult | None = None
        last_valid_context: QualityContext | None = None
        latest_result: AgentResult | None = None
        latest_context: QualityContext | None = None
        max_attempts = self._max_retries + 1

        while attempts < max_attempts:
            attempts += 1
            error_message: str | None = None

            if initial_snapshot is not None and attempts > 1:
                self._restore_state(state, initial_snapshot)

            try:
                agent.execute(*args, **kwargs)
                agent_result = agent.last_result
                if agent_result is None:
                    agent_result = AgentResult.failure_result(
                        agent_name=agent.name,
                        output="Agente sin AgentResult",
                        issues=["last_result no disponible"],
                    )
            except Exception as exc:
                error_message = str(exc)
                agent_result = AgentResult.failure_result(
                    agent_name=agent.name,
                    output=f"Error durante ejecución: {exc}",
                    issues=[str(exc)],
                )

            quality_context = self._quality_pipeline.evaluate(
                agent_result,
                objective=objective,
            )
            quality_decision = quality_context.quality_decision
            if quality_decision is None:
                raise ValueError("QualityPipeline no produjo una QualityDecision")

            history_entry: dict[str, Any] = {
                "attempt": attempts,
                "agent_result": agent_result.to_dict(),
                "quality_context": quality_context.to_dict(),
            }
            if error_message is not None:
                history_entry["error"] = error_message
            history.append(history_entry)

            latest_result = agent_result
            latest_context = quality_context

            if agent_result.success:
                last_valid_result = agent_result
                last_valid_context = quality_context
                if state is not None:
                    success_snapshot = deepcopy(state)

            if not self._retry_policy.should_retry(quality_decision, retry_count):
                break

            retry_count += 1

        final_result, final_context = self._resolve_final_output(
            latest_result=latest_result,
            latest_context=latest_context,
            last_valid_result=last_valid_result,
            last_valid_context=last_valid_context,
        )

        if state is not None:
            if not final_result.success and success_snapshot is not None:
                self._restore_state(state, success_snapshot)
            elif (
                not latest_result.success
                and last_valid_result is not None
                and success_snapshot is not None
            ):
                self._restore_state(state, success_snapshot)

        return RetryResult(
            final_result=final_result,
            attempts=attempts,
            quality_context=final_context,
            history=history,
        )

    def _resolve_final_output(
        self,
        *,
        latest_result: AgentResult | None,
        latest_context: QualityContext | None,
        last_valid_result: AgentResult | None,
        last_valid_context: QualityContext | None,
    ) -> tuple[AgentResult, QualityContext]:
        if latest_result is None or latest_context is None:
            raise ValueError("No hubo intentos de ejecución")

        if not latest_result.success and last_valid_result is not None:
            assert last_valid_context is not None
            return last_valid_result, last_valid_context

        return latest_result, latest_context

    def _find_project_state(self, *args: Any, **kwargs: Any) -> ProjectState | None:
        for value in args:
            if isinstance(value, ProjectState):
                return value

        state = kwargs.get("state")
        if isinstance(state, ProjectState):
            return state

        return None

    def _restore_state(self, target: ProjectState, snapshot: ProjectState) -> None:
        restored = deepcopy(snapshot)
        for field in fields(ProjectState):
            setattr(target, field.name, getattr(restored, field.name))

    def _extract_objective(self, *args: Any, **kwargs: Any) -> str:
        for value in args:
            if isinstance(value, ProjectState):
                return value.description or ""

        state = kwargs.get("state")
        if isinstance(state, ProjectState):
            return state.description or ""

        objective = kwargs.get("objective")
        if isinstance(objective, str):
            return objective

        return ""
