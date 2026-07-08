from agents.analyst_agent import AnalystAgent
from agents.architect_agent import ArchitectAgent
from agents.base_agent import BaseAgent
from agents.developer_agent import DeveloperAgent
from agents.qa_agent import QAAgent
from context.agent_context import AgentContext
from state.project_state import ProjectState


class ContextBuilder:
    """Construye AgentContext filtrado desde ProjectState según el rol del agente."""

    @staticmethod
    def build(agent: BaseAgent, state: ProjectState) -> AgentContext:
        builders = {
            AnalystAgent: ContextBuilder.for_analyst,
            ArchitectAgent: ContextBuilder.for_architect,
            DeveloperAgent: ContextBuilder.for_developer,
            QAAgent: ContextBuilder.for_qa,
        }
        builder = builders.get(type(agent))
        if builder is None:
            raise ValueError(f"No hay builder de contexto para {type(agent).__name__}")
        return builder(state)

    @staticmethod
    def for_analyst(state: ProjectState) -> AgentContext:
        return AgentContext(
            agent_name="Business Analyst",
            role="Generar historias de usuario a partir de los requerimientos del proyecto",
            inputs={
                "project_name": state.project_name,
                "description": state.description,
                "requirements": list(state.requirements),
            },
            constraints=[
                "No definir arquitectura técnica",
                "Usar formato: Como usuario quiero...",
                "Basarse en la descripción y requerimientos del proyecto",
            ],
        )

    @staticmethod
    def for_architect(state: ProjectState) -> AgentContext:
        return AgentContext(
            agent_name="Software Architect",
            role="Generar el Software Design Document del proyecto",
            inputs={
                "project_name": state.project_name,
                "description": state.description,
                "user_stories": list(state.user_stories),
            },
            constraints=[
                "Basarse en las historias de usuario existentes",
                "Definir stack técnico y patrones de arquitectura",
                "No generar código ni tareas de implementación",
            ],
        )

    @staticmethod
    def for_developer(state: ProjectState) -> AgentContext:
        return AgentContext(
            agent_name="Flutter Developer",
            role="Generar tareas de desarrollo y acciones basadas en el SDD",
            inputs={
                "project_name": state.project_name,
                "description": state.description,
                "software_design_document": state.software_design_document,
                "architecture": state.architecture,
                "user_stories": list(state.user_stories),
            },
            constraints=[
                "Seguir la arquitectura definida en el SDD",
                "No modificar el Software Design Document",
                "Generar tareas y acciones, no ejecutar herramientas directamente",
            ],
        )

    @staticmethod
    def for_qa(state: ProjectState) -> AgentContext:
        return AgentContext(
            agent_name="QA Engineer",
            role="Validar la completitud y calidad de los artefactos del proyecto",
            inputs={
                "user_stories_count": len(state.user_stories),
                "has_architecture": bool(state.architecture),
                "tasks_count": len(state.tasks),
                "generated_files_count": len(state.generated_files),
                "has_sdd": bool(state.software_design_document),
            },
            constraints=[
                "No modificar artefactos del proyecto",
                "Validar presencia de historias, arquitectura y tareas",
                "Generar un reporte de calidad estructurado",
            ],
        )
