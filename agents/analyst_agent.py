from agents.base_agent import BaseAgent
from context.agent_context import AgentContext
from memory.agent_memory import AgentMemory
from state.project_state import ProjectState


class AnalystAgent(BaseAgent):
    """Agente que analiza la descripción del proyecto y genera historias de usuario."""

    @property
    def name(self) -> str:
        return "Business Analyst"

    @property
    def uses_llm_pipeline(self) -> bool:
        return True

    def process(self, state: ProjectState) -> ProjectState:
        """Reservado para compatibilidad; AnalystAgent usa process_with_llm."""
        return state

    def process_with_llm(
        self,
        context: AgentContext,
        memory: AgentMemory,
        state: ProjectState,
    ) -> ProjectState:
        state.logs.append(f"[{self.name}] Analizando descripción del proyecto")
        state.logs.append(
            f"[{self.name}] Descripción: "
            f"{context.inputs.get('description', 'Sin descripción')}"
        )
        state.logs.append(f"[{self.name}] Ejecutando pipeline LLM")

        parsed = self._execute_llm_pipeline(context, memory)
        user_stories = parsed["user_stories"]

        state.user_stories.extend(user_stories)
        memory.add_note(f"Generadas {len(user_stories)} historias de usuario")

        state.logs.append(
            f"[{self.name}] Generadas {len(user_stories)} historias de usuario via LLM"
        )
        return state

    def build_output_summary(self, state: ProjectState) -> str:
        return f"{len(state.user_stories)} historias de usuario generadas"
