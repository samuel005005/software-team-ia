from actions.action_executor import ActionExecutor
from agents.base_agent import BaseAgent
from state.project_state import ProjectState
from tools.tool_executor import ToolExecutor


class Orchestrator:
    """Coordina la ejecución secuencial de agentes y acciones sobre un ProjectState compartido."""

    def __init__(
        self,
        agents: list[BaseAgent],
        tool_executor: ToolExecutor | None = None,
        action_executor: ActionExecutor | None = None,
    ) -> None:
        self._agents = agents
        self._tool_executor = tool_executor
        self._action_executor = action_executor or (
            ActionExecutor(tool_executor) if tool_executor else None
        )

    def run(self, state: ProjectState) -> ProjectState:
        """Ejecuta todos los agentes en orden y procesa las acciones pendientes."""
        state.status = "RUNNING"

        for agent in self._agents:
            agent.execute(state)
            self._execute_pending_actions(state)

        state.current_agent = None
        state.status = "COMPLETED"
        return state

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
