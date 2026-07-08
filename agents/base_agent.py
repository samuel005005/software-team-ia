from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from agents.agent_result import AgentResult
from context.agent_context import AgentContext
from execution.execution_record import ExecutionRecord, ExecutionStatus
from llm.base_provider import LLMProvider
from memory.agent_memory import AgentMemory
from memory.memory_store import MemoryStore
from parsers.response_parser import ResponseParser
from prompts.prompt_builder import PromptBuilder
from state.project_state import ProjectState


class BaseAgent(ABC):
    """Clase base abstracta para todos los agentes del sistema."""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        memory_store: MemoryStore | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._memory_store = memory_store
        self._last_result: AgentResult | None = None

    @property
    def last_result(self) -> AgentResult | None:
        """Último resultado estructurado producido por execute()."""
        return self._last_result

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre identificador del agente."""
        ...

    @property
    def uses_llm_pipeline(self) -> bool:
        """Indica si el agente utiliza el pipeline Context → Prompt → LLM → Parser."""
        return False

    def execute(self, state: ProjectState) -> ProjectState:
        """Ejecuta el agente registrando su historial de ejecución."""
        state.current_agent = self.name
        state.logs.append(f"[{self.name}] Inicio de ejecución")

        input_summary = self.build_input_summary(state)
        started_at = datetime.now()
        errors: list[str] = []
        status = ExecutionStatus.SUCCESS
        output_summary = ""

        try:
            if self.uses_llm_pipeline:
                from context.context_builder import ContextBuilder

                context = ContextBuilder.build(self, state)
                memory = self._get_memory()
                input_summary = self.build_input_summary(state, context)
                state = self.process_with_llm(context, memory, state)
            else:
                state = self.process(state)

            output_summary = self.build_output_summary(state)
            state.logs.append(f"[{self.name}] Ejecución completada")
        except Exception as exc:
            status = ExecutionStatus.FAILED
            errors.append(str(exc))
            output_summary = f"Error durante ejecución: {exc}"
            state.logs.append(f"[{self.name}] Error: {exc}")

        record = ExecutionRecord(
            agent_name=type(self).__name__,
            started_at=started_at,
            finished_at=datetime.now(),
            input_summary=input_summary,
            output_summary=output_summary,
            status=status,
            errors=errors,
        )
        state.execution_history.add(record)

        if status == ExecutionStatus.SUCCESS:
            state.logs.append(
                f"[ExecutionHistory] {type(self).__name__} ejecutado correctamente"
            )
        else:
            state.logs.append(
                f"[ExecutionHistory] {type(self).__name__} falló durante la ejecución"
            )

        self._last_result = self.build_agent_result(
            success=status == ExecutionStatus.SUCCESS,
            output=output_summary,
            errors=errors,
        )

        return state

    def build_agent_result(
        self,
        *,
        success: bool,
        output: str,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
        confidence: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentResult:
        """Construye un AgentResult estándar para el agente actual."""
        if success:
            return AgentResult.success_result(
                agent_name=self.name,
                output=output,
                confidence=1.0 if confidence is None else confidence,
                warnings=warnings,
                metadata=metadata,
            )

        return AgentResult.failure_result(
            agent_name=self.name,
            output=output,
            issues=errors,
            warnings=warnings,
            metadata=metadata,
        )

    def _get_memory(self) -> AgentMemory:
        if self._memory_store is None:
            return AgentMemory(agent_name=self.name)
        return self._memory_store.get(self.name)

    def _execute_llm_pipeline(
        self,
        context: AgentContext,
        memory: AgentMemory,
    ) -> dict[str, Any]:
        if self._llm_provider is None:
            raise ValueError(f"{self.name} requiere un LLMProvider para el pipeline LLM")

        request = PromptBuilder.build(context)
        memory.add_note(f"Prompt generado para {context.agent_name}")

        response = self._llm_provider.generate(request)
        memory.add_note(
            f"Respuesta LLM recibida de {response.provider} "
            f"({response.duration_ms}ms)"
        )

        parsed = ResponseParser.parse(self.name, response)
        memory.add_decision(f"Respuesta parseada para {context.agent_name}")
        return parsed

    @abstractmethod
    def process(self, state: ProjectState) -> ProjectState:
        """Implementa la lógica específica del agente sin pipeline LLM."""
        ...

    def process_with_llm(
        self,
        context: AgentContext,
        memory: AgentMemory,
        state: ProjectState,
    ) -> ProjectState:
        """Implementa la lógica del agente usando el pipeline LLM."""
        raise NotImplementedError(
            f"{type(self).__name__} no implementa process_with_llm"
        )

    def build_input_summary(
        self,
        state: ProjectState,
        context: AgentContext | None = None,
    ) -> str:
        if context is not None:
            return (
                f"project={context.inputs.get('project_name')}, "
                f"agent={context.agent_name}, "
                f"pipeline=llm"
            )
        return (
            f"project={state.project_name}, "
            f"user_stories={len(state.user_stories)}, "
            f"tasks={len(state.tasks)}"
        )

    def build_output_summary(self, state: ProjectState) -> str:
        return "Ejecución completada"
