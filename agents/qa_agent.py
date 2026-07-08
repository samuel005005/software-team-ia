from agents.base_agent import BaseAgent
from context.agent_context import AgentContext
from memory.agent_memory import AgentMemory
from state.project_state import ProjectState


class QAAgent(BaseAgent):
    """Agente que valida la completitud del trabajo previo y genera un reporte QA."""

    @property
    def name(self) -> str:
        return "QA Engineer"

    @property
    def uses_llm_pipeline(self) -> bool:
        return True

    def process(self, state: ProjectState) -> ProjectState:
        """Reservado para compatibilidad; QAAgent usa process_with_llm."""
        return state

    def process_with_llm(
        self,
        context: AgentContext,
        memory: AgentMemory,
        state: ProjectState,
    ) -> ProjectState:
        inputs = context.inputs
        state.logs.append(f"[{self.name}] Iniciando revisión de calidad")
        state.logs.append(
            f"[{self.name}] Artefactos: "
            f"historias={inputs.get('user_stories_count', 0)}, "
            f"arquitectura={'sí' if inputs.get('has_architecture') else 'no'}, "
            f"tareas={inputs.get('tasks_count', 0)}, "
            f"archivos={inputs.get('generated_files_count', 0)}"
        )
        state.logs.append(f"[{self.name}] Ejecutando pipeline LLM")

        parsed = self._execute_llm_pipeline(context, memory)
        qa_report = parsed["qa_report"]
        qa_report_text = parsed["qa_report_text"]

        state.qa_report = qa_report_text
        memory.add_note("QA report generado mediante LLM")

        checks_passed = qa_report.get("checks_passed", 0)
        checks_total = qa_report.get("checks_total", 0)
        state.logs.append(
            f"[{self.name}] Reporte QA generado: {checks_passed}/{checks_total} OK via LLM"
        )

        return state

    def build_output_summary(self, state: ProjectState) -> str:
        return "Reporte QA generado" if state.qa_report else "Sin reporte QA"
