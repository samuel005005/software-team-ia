from typing import Any

from agents.base_agent import BaseAgent
from context.agent_context import AgentContext
from memory.agent_memory import AgentMemory
from state.project_state import ProjectState


class ArchitectAgent(BaseAgent):
    """Agente que analiza las historias de usuario y genera el Software Design Document."""

    @property
    def name(self) -> str:
        return "Software Architect"

    @property
    def uses_llm_pipeline(self) -> bool:
        return True

    def process(self, state: ProjectState) -> ProjectState:
        """Reservado para compatibilidad; ArchitectAgent usa process_with_llm."""
        return state

    def process_with_llm(
        self,
        context: AgentContext,
        memory: AgentMemory,
        state: ProjectState,
    ) -> ProjectState:
        state.logs.append(
            f"[{self.name}] Analizando {len(context.inputs.get('user_stories', []))} "
            "historias de usuario"
        )
        state.logs.append(f"[{self.name}] Ejecutando pipeline LLM")

        parsed = self._execute_llm_pipeline(context, memory)

        architecture_summary = parsed["architecture_summary"]
        software_design_document = parsed["software_design_document"]
        if not software_design_document:
            software_design_document = self._build_sdd_from_parsed(parsed, context)

        state.architecture = architecture_summary
        state.software_design_document = software_design_document

        memory.add_note("SDD y arquitectura generados via LLM")
        memory.add_decision(
            f"Patrones seleccionados: {', '.join(parsed.get('patterns', []))}"
        )

        state.logs.append(f"[{self.name}] Software Design Document generado")
        state.logs.append(f"[{self.name}] Arquitectura general definida en el SDD")
        state.logs.append(f"[{self.name}] SDD generado via LLM")

        return state

    def _build_sdd_from_parsed(
        self,
        parsed: dict[str, Any],
        context: AgentContext,
    ) -> str:
        architecture = parsed["architecture"]
        patterns = parsed.get("patterns", [])
        patterns_section = "\n".join(f"  - {pattern}" for pattern in patterns) or "  - N/A"
        user_stories = context.inputs.get("user_stories", [])
        user_stories_section = "\n".join(
            f"  - {story}" for story in user_stories
        ) or "  - Sin historias definidas"

        return (
            "SOFTWARE DESIGN DOCUMENT (SDD)\n"
            "==============================\n\n"
            "1. INFORMACIÓN DEL PROYECTO\n"
            "-----------------------------\n"
            f"Nombre: {context.inputs.get('project_name', 'Proyecto sin nombre')}\n"
            f"Descripción: {context.inputs.get('description', 'Sin descripción')}\n\n"
            "Historias de usuario analizadas:\n"
            f"{user_stories_section}\n\n"
            "2. ARQUITECTURA GENERAL\n"
            "-----------------------\n"
            f"Frontend:\n{architecture.get('frontend', 'N/A')}\n\n"
            f"Backend:\n{architecture.get('backend', 'N/A')}\n\n"
            f"Database:\n{architecture.get('database', 'N/A')}\n\n"
            "3. PATRONES\n"
            "-----------\n"
            f"{patterns_section}"
        )

    def build_output_summary(self, state: ProjectState) -> str:
        return (
            "SDD y arquitectura definidos"
            if state.software_design_document
            else "Sin SDD generado"
        )
