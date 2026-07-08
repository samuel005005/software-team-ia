from datetime import datetime

from actions.action_executor import ActionExecutor
from agents.base_agent import BaseAgent
from execution.execution_record import ExecutionRecord, ExecutionStatus
from execution.retry_executor import RetryExecutor
from execution.retry_result import RetryResult
from state.project_state import ProjectState
from tools.tool_executor import ToolExecutor


class Orchestrator:
    """Coordina la ejecución secuencial de agentes y acciones sobre un ProjectState compartido."""

    def __init__(
        self,
        agents: list[BaseAgent],
        tool_executor: ToolExecutor | None = None,
        action_executor: ActionExecutor | None = None,
        retry_executor: RetryExecutor | None = None,
    ) -> None:
        self._agents = agents
        self._tool_executor = tool_executor
        self._action_executor = action_executor or (
            ActionExecutor(tool_executor) if tool_executor else None
        )
        self._retry_executor = retry_executor or RetryExecutor()

    def run(self, state: ProjectState) -> ProjectState:
        """Ejecuta todos los agentes en orden y procesa las acciones pendientes."""
        state.status = "RUNNING"

        for agent in self._agents:
            history_start = len(state.execution_history.get_all())
            retry_result = self._retry_executor.execute(agent, state)
            self._register_retry_execution(
                state,
                agent,
                retry_result,
                history_start,
            )
            agent._last_result = retry_result.final_result
            self._execute_pending_actions(state)

        state.current_agent = None
        state.status = "COMPLETED"
        return state

    def _register_retry_execution(
        self,
        state: ProjectState,
        agent: BaseAgent,
        retry_result: RetryResult,
        history_start: int,
    ) -> None:
        attempt_records = state.execution_history.get_all()[history_start:]
        state.execution_history.discard_from(history_start)

        quality_decision = retry_result.quality_context.quality_decision
        quality_score = quality_decision.score if quality_decision is not None else 0.0
        retry_count = max(0, retry_result.attempts - 1)

        started_at = (
            attempt_records[0].started_at
            if attempt_records
            else datetime.now()
        )
        final_result = retry_result.final_result

        record = ExecutionRecord(
            agent_name=type(agent).__name__,
            started_at=started_at,
            finished_at=datetime.now(),
            input_summary=attempt_records[0].input_summary if attempt_records else "",
            output_summary=final_result.output,
            status=(
                ExecutionStatus.SUCCESS
                if final_result.success
                else ExecutionStatus.FAILED
            ),
            errors=list(final_result.issues),
            metadata={
                "attempts": retry_result.attempts,
                "quality_score": quality_score,
                "retry_count": retry_count,
                "retry_history": retry_result.history,
            },
        )
        state.execution_history.add(record)

    def _execute_pending_actions(self, state: ProjectState) -> None:
        if not state.actions:
            return

        if self._action_executor is None:
            state.logs.append(
                "[orchestrator] Acciones pendientes sin ActionExecutor disponible"
            )
            return

        pending_actions = list(state.actions)
        state.actions.clear()

        self._action_executor.execute(pending_actions, state)
