from actions.file_actions import CreateDirectoryAction, CreateFileAction
from agents.base_agent import BaseAgent
from context.agent_context import AgentContext
from memory.agent_memory import AgentMemory
from state.project_state import ProjectState


class DeveloperAgent(BaseAgent):
    """Agente que genera tareas de desarrollo y define acciones a ejecutar."""

    @property
    def name(self) -> str:
        return "Flutter Developer"

    @property
    def uses_llm_pipeline(self) -> bool:
        return True

    def process(self, state: ProjectState) -> ProjectState:
        """Reservado para compatibilidad; DeveloperAgent usa process_with_llm."""
        return state

    def process_with_llm(
        self,
        context: AgentContext,
        memory: AgentMemory,
        state: ProjectState,
    ) -> ProjectState:
        sdd = context.inputs.get("software_design_document") or state.software_design_document
        if not sdd:
            state.logs.append(
                f"[{self.name}] Advertencia: no se encontró Software Design Document"
            )
            return state

        state.logs.append(
            f"[{self.name}] Trabajando basado en arquitectura definida por Software Architect"
        )
        state.logs.append(f"[{self.name}] Leyendo Software Design Document")
        state.logs.append(f"[{self.name}] Ejecutando pipeline LLM")

        parsed = self._execute_llm_pipeline(context, memory)
        tasks = parsed["tasks"]

        state.tasks = tasks
        memory.add_note(f"Generadas {len(tasks)} tareas de desarrollo via LLM")

        state.logs.append(
            f"[{self.name}] Generadas {len(tasks)} tareas basadas en el SDD via LLM"
        )

        self._queue_project_actions(state)

        return state

    def build_output_summary(self, state: ProjectState) -> str:
        return f"{len(state.tasks)} tareas creadas"

    def _queue_project_actions(self, state: ProjectState) -> None:
        project_slug = state.project_name or "proyecto"
        project_base = f"projects/{project_slug}"

        readme_content = (
            f"# {state.project_name or 'Proyecto'}\n\n"
            f"## Descripción\n"
            f"{state.description or 'Sin descripción'}\n\n"
            f"## Arquitectura\n"
            f"{state.architecture or 'No definida'}\n\n"
            f"## Tecnologías\n"
            f"- Flutter + Riverpod\n"
            f"- FastAPI\n"
            f"- PostgreSQL\n"
        )

        state.actions.extend(
            [
                CreateDirectoryAction(f"{project_base}/lib"),
                CreateFileAction(f"{project_base}/README.md", readme_content),
            ]
        )

        state.logs.append(
            f"[{self.name}] Generadas {len(state.actions)} acciones para ejecución"
        )
