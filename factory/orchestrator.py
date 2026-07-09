from pathlib import Path

from factory.agent_runner import run_cursor_agent
from factory.analysis_store import analysis_path, load_analysis, save_analysis
from factory.config import DOCS_DIR, model_for_role
from factory.models import FactoryRole, ModelTier, RunResult, TaskItem, TaskStatus
from factory.progress import ProgressReporter
from factory.prompt_builder import build_analyze_prompt, build_role_prompt
from factory.state_store import append_run
from factory.task_parser import load_tasks, mark_task_status, next_pending_task

TASKS_PATH = DOCS_DIR / "TASKS.md"


class SDDOrchestrator:
    """Orquestador SDD: encadena roles vía Cursor SDK."""

    def __init__(
        self,
        *,
        tasks_path: Path = TASKS_PATH,
        dry_run: bool = False,
        progress: ProgressReporter | None = None,
        tier: ModelTier | None = None,
    ) -> None:
        self._tasks_path = tasks_path
        self._dry_run = dry_run
        self._progress = progress or ProgressReporter()
        self._tier = tier

    def list_pending(self) -> list[TaskItem]:
        return [t for t in load_tasks(self._tasks_path) if t.status == TaskStatus.PENDING]

    def _get_task(self, task_id: str) -> TaskItem:
        task = next((t for t in load_tasks(self._tasks_path) if t.task_id == task_id), None)
        if task is None:
            raise ValueError(f"Tarea {task_id} no encontrada en TASKS.md")
        if task.status == TaskStatus.COMPLETED:
            raise ValueError(f"Tarea {task_id} ya está completada")
        return task

    def run_role(
        self,
        role: FactoryRole,
        *,
        task: TaskItem | None = None,
        extra_instruction: str | None = None,
        tier: ModelTier | None = None,
        analysis_context: str | None = None,
        prompt: str | None = None,
    ) -> RunResult:
        resolved_tier = tier or self._tier

        if task:
            self._progress.phase(f"Preparando {task.task_id}: {task.title}")
        else:
            self._progress.phase(f"Preparando rol {role.value}")

        model = model_for_role(role, tier=resolved_tier)
        if prompt is None:
            self._progress.info("Construyendo prompt con rules, skills y docs…")
            prompt = build_role_prompt(
                role,
                task=task,
                extra_instruction=extra_instruction,
                analysis_context=analysis_context,
            )
        self._progress.info(f"Prompt listo ({len(prompt)} caracteres)")
        self._progress.info(f"Modelo ({resolved_tier or 'auto'}): {model}")

        result = run_cursor_agent(
            prompt,
            role=role,
            task_id=task.task_id if task else None,
            model=model,
            dry_run=self._dry_run,
            progress=self._progress,
        )
        if not self._dry_run:
            append_run(result)
        return result

    def run_analyze_task(self, task_id: str) -> RunResult:
        """Fase 1: analiza requerimiento (modelo smart). No implementa."""
        task = self._get_task(task_id)
        self._progress.phase(f"Análisis de requerimiento — {task_id}")

        prompt = build_analyze_prompt(task)
        result = self.run_role(
            FactoryRole.ARCHITECT,
            task=task,
            tier="smart",
            prompt=prompt,
        )

        if self._dry_run or result.status == "error":
            return result

        if analysis_path(task_id).exists():
            self._progress.success(f"Análisis guardado en {analysis_path(task_id)}")
        elif result.summary:
            save_analysis(task_id, result.summary)
            self._progress.success(f"Análisis guardado en {analysis_path(task_id)}")

        return result

    def run_developer_next(self, *, mark_in_progress: bool = True) -> RunResult:
        task = next_pending_task(self._tasks_path)
        if task is None:
            self._progress.info("No hay tareas pendientes en docs/TASKS.md")
            return RunResult(
                role=FactoryRole.DEVELOPER,
                task_id=None,
                status="no_tasks",
                agent_id=None,
                summary="No hay tareas pendientes en docs/TASKS.md",
            )

        if mark_in_progress and not self._dry_run:
            self._progress.info(f"Marcando {task.task_id} como [~] en TASKS.md")
            mark_task_status(self._tasks_path, task.task_id, TaskStatus.IN_PROGRESS)

        return self.run_role(FactoryRole.DEVELOPER, task=task)

    def run_developer_task(
        self,
        task_id: str,
        *,
        mark_in_progress: bool = True,
        analysis_context: str | None = None,
        tier: ModelTier | None = None,
    ) -> RunResult:
        task = self._get_task(task_id)

        if mark_in_progress and not self._dry_run and task.status == TaskStatus.PENDING:
            self._progress.info(f"Marcando {task.task_id} como [~] en TASKS.md")
            mark_task_status(self._tasks_path, task.task_id, TaskStatus.IN_PROGRESS)

        return self.run_role(
            FactoryRole.DEVELOPER,
            task=task,
            analysis_context=analysis_context,
            tier=tier or self._tier,
        )

    def run_full_task(
        self,
        task_id: str,
        *,
        mark_in_progress: bool = True,
        skip_analyze: bool = False,
    ) -> list[RunResult]:
        """Un solo comando: Analizar (smart) → Crear + Probar (fast)."""
        results: list[RunResult] = []

        if mark_in_progress and not self._dry_run:
            task = self._get_task(task_id)
            if task.status == TaskStatus.PENDING:
                self._progress.info(f"Marcando {task_id} como [~] en TASKS.md")
                mark_task_status(self._tasks_path, task_id, TaskStatus.IN_PROGRESS)

        if not skip_analyze:
            self._progress.phase(f"═══ Paso 1/2: Análisis ({task_id}) ═══")
            analyze_result = self.run_analyze_task(task_id)
            results.append(analyze_result)
            if analyze_result.status == "error":
                return results

        analysis = load_analysis(task_id)
        self._progress.phase(f"═══ Paso 2/2: Implementar + Probar ({task_id}) ═══")
        dev_result = self.run_developer_task(
            task_id,
            mark_in_progress=False,
            analysis_context=analysis,
            tier="fast",
        )
        results.append(dev_result)
        return results

    def run_pipeline(
        self,
        *,
        max_dev_tasks: int = 1,
        include_qa: bool = True,
        include_review: bool = False,
        include_security: bool = False,
    ) -> list[RunResult]:
        """Pipeline automático: Developer (N tareas) → QA → Review → Security."""
        results: list[RunResult] = []

        for _ in range(max_dev_tasks):
            pending_before = self.list_pending()
            if not pending_before:
                break
            results.append(self.run_developer_next())
            if results[-1].status == "no_tasks":
                break

        if include_qa and (not self.list_pending() or max_dev_tasks == 0):
            results.append(
                self.run_role(
                    FactoryRole.QA,
                    extra_instruction="Valida las tareas completadas recientemente contra SPEC.",
                )
            )

        if include_review:
            results.append(self.run_role(FactoryRole.REVIEWER))

        if include_security:
            results.append(self.run_role(FactoryRole.SECURITY))

        return results
