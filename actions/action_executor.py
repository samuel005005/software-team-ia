from actions.base_action import BaseAction
from actions.file_actions import CreateDirectoryAction, CreateFileAction
from state.project_state import ProjectState
from tools.tool_executor import ToolExecutor


class ActionExecutor:
    """Ejecuta las acciones generadas por los agentes usando el ToolExecutor."""

    def __init__(self, tool_executor: ToolExecutor) -> None:
        self._tool_executor = tool_executor

    def execute(self, actions: list[BaseAction], state: ProjectState) -> None:
        """Recorre y ejecuta cada acción, capturando errores y registrando logs."""
        for action in actions:
            action_name = type(action).__name__
            state.logs.append(f"[ActionExecutor] Ejecutando {action_name}")

            try:
                result = action.execute(self._tool_executor)

                for log in result.get("logs", []):
                    state.logs.append(log)

                if result.get("success"):
                    self._log_success(state, action)
                    self._update_state(state, action)
                else:
                    error = result.get("error", "operación fallida")
                    state.logs.append(
                        f"[ActionExecutor] Error al ejecutar {action_name}: {error}"
                    )

            except Exception as exc:
                state.logs.append(
                    f"[ActionExecutor] Excepción en {action_name}: {exc}"
                )

    def _log_success(self, state: ProjectState, action: BaseAction) -> None:
        if isinstance(action, CreateFileAction):
            state.logs.append("[ActionExecutor] Archivo creado correctamente")
        elif isinstance(action, CreateDirectoryAction):
            state.logs.append("[ActionExecutor] Directorio creado correctamente")
        else:
            state.logs.append(f"[ActionExecutor] Acción {action.name} completada")

    def _update_state(self, state: ProjectState, action: BaseAction) -> None:
        if isinstance(action, CreateFileAction):
            state.generated_files.append(
                {"path": action.path, "content": action.content}
            )
