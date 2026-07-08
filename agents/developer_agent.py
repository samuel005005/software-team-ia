from agents.base_agent import BaseAgent
from artifacts.artifact_collection import ArtifactCollection
from artifacts.artifact_writer import ArtifactWriter
from artifacts.developer_fallback import build_fallback_collection
from context.agent_context import AgentContext
from memory.agent_memory import AgentMemory
from parsers import developer_parser
from prompts import developer_code_prompt
from state.project_state import ProjectState


class DeveloperAgent(BaseAgent):
    """Agente que genera tareas de desarrollo y persiste artefactos de código."""

    def __init__(
        self,
        llm_provider=None,
        memory_store=None,
        artifact_writer: ArtifactWriter | None = None,
    ) -> None:
        super().__init__(llm_provider=llm_provider, memory_store=memory_store)
        self._artifact_writer = artifact_writer
        self._last_artifacts = ArtifactCollection()
        self._last_artifact_source = "developer_v1"

    @property
    def last_artifacts(self) -> ArtifactCollection:
        """Última colección de artefactos generada por el agente."""
        return self._last_artifacts

    @property
    def last_artifact_source(self) -> str:
        """Fuente de la última colección de artefactos."""
        return self._last_artifact_source

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
        state.logs.append(f"[{self.name}] Ejecutando pipeline LLM de tareas")

        parsed = self._execute_llm_pipeline(context, memory)
        tasks = parsed["tasks"]

        state.tasks = tasks
        memory.add_note(f"Generadas {len(tasks)} tareas de desarrollo via LLM")

        state.logs.append(
            f"[{self.name}] Generadas {len(tasks)} tareas basadas en el SDD via LLM"
        )

        artifacts, source = self._generate_artifacts(state, tasks)
        self._last_artifacts = artifacts
        self._last_artifact_source = source
        self._persist_artifacts(state, artifacts)

        return state

    def build_output_summary(self, state: ProjectState) -> str:
        artifact_count = len(self._last_artifacts.artifacts)
        return (
            f"{len(state.tasks)} tareas creadas, "
            f"{artifact_count} artefactos generados ({self._last_artifact_source})"
        )

    def _generate_artifacts(
        self,
        state: ProjectState,
        tasks: list,
    ) -> tuple[ArtifactCollection, str]:
        project_slug = state.project_name or "proyecto"

        if self._llm_provider is None:
            return build_fallback_collection(state, tasks), "developer_fallback"

        try:
            request = developer_code_prompt.build(
                objective=state.description or "",
                project_name=project_slug,
                software_design_document=state.software_design_document or "",
                tasks=tasks,
                architecture=state.architecture or "",
            )
            state.logs.append(f"[{self.name}] Ejecutando pipeline LLM de código")
            response = self._llm_provider.generate(request)
            artifacts = developer_parser.parse_artifacts(
                response,
                project_slug=project_slug,
            )
            state.logs.append(
                f"[{self.name}] Generados {len(artifacts.artifacts)} artefactos via LLM"
            )
            return artifacts, "developer_llm"
        except Exception as exc:
            state.logs.append(
                f"[{self.name}] Fallback de artefactos por error en generación LLM: {exc}"
            )
            return build_fallback_collection(state, tasks), "developer_fallback"

    def _persist_artifacts(
        self,
        state: ProjectState,
        artifacts: ArtifactCollection,
    ) -> None:
        if self._artifact_writer is None:
            state.logs.append(
                f"[{self.name}] ArtifactWriter no configurado; artefactos no persistidos"
            )
            return

        results = self._artifact_writer.write_all(artifacts)
        for artifact, result in zip(artifacts.artifacts, results, strict=True):
            if result.success:
                state.generated_files.append(
                    {
                        "path": artifact.path,
                        "content": artifact.content,
                    }
                )
                state.logs.append(
                    f"[{self.name}] Artefacto persistido: {artifact.path}"
                )
            else:
                state.logs.append(
                    f"[{self.name}] Error al persistir {artifact.path}: {result.error}"
                )

        state.logs.append(
            f"[{self.name}] Persistidos {len(results)} artefactos via ToolRegistry"
        )
