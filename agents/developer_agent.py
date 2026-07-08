from actions.file_actions import CreateDirectoryAction, CreateFileAction
from agents.base_agent import BaseAgent
from state.project_state import ProjectState


class DeveloperAgent(BaseAgent):
    """Agente que genera tareas de desarrollo y define acciones a ejecutar."""

    @property
    def name(self) -> str:
        return "Flutter Developer"

    def process(self, state: ProjectState) -> ProjectState:
        sdd = state.software_design_document
        if not sdd:
            state.logs.append(
                f"[{self.name}] Advertencia: no se encontró Software Design Document"
            )
            return state

        state.logs.append(
            f"[{self.name}] Trabajando basado en arquitectura definida por Software Architect"
        )
        state.logs.append(f"[{self.name}] Leyendo Software Design Document")

        state.tasks = [
            {
                "id": 1,
                "title": "Configurar estructura Flutter Feature First",
                "description": "Crear carpetas lib/core, lib/features y lib/shared con Clean Architecture",
                "status": "pending",
            },
            {
                "id": 2,
                "title": "Configurar Riverpod",
                "description": "Implementar gestión de estado según arquitectura Flutter del SDD",
                "status": "pending",
            },
            {
                "id": 3,
                "title": "Implementar autenticación JWT",
                "description": "Registro, inicio de sesión y Secure Storage en el cliente",
                "status": "pending",
            },
            {
                "id": 4,
                "title": "Crear módulo de gestión de perfil",
                "description": "Feature de usuario con validación de entradas",
                "status": "pending",
            },
            {
                "id": 5,
                "title": "Configurar API FastAPI",
                "description": "Estructura routers, services, repositories y models",
                "status": "pending",
            },
            {
                "id": 6,
                "title": "Configurar PostgreSQL",
                "description": "Modelos de datos y repositorios para persistencia",
                "status": "pending",
            },
            {
                "id": 7,
                "title": "Implementar suite de pruebas",
                "description": "Unit Tests e Integration Tests según SDD",
                "status": "pending",
            },
        ]

        state.logs.append(
            f"[{self.name}] Generadas {len(state.tasks)} tareas basadas en el SDD"
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
