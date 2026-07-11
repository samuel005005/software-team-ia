from pathlib import Path

from factory.agent_runner import AgentPhase, run_cursor_agent_session
from factory.analysis_store import (
    analysis_path,
    has_analysis,
    load_analysis,
    save_analysis,
    save_story_analysis,
    story_analysis_path,
)
from factory.config import (
    DOCS_DIR,
    auto_release_enabled,
    auto_release_include_review,
    auto_release_include_security,
    model_for_role,
    single_session_enabled,
)
from factory.gate_parser import evaluate_gate
from factory.models import FactoryRole, GateResult, ModelTier, QAScope, RunResult, TaskItem, TaskStatus
from factory.progress import ProgressReporter
from factory.prompt_builder import (
    build_analyze_batch_prompt,
    build_analyze_prompt,
    build_closure_prompt,
    build_dev_followup_prompt,
    build_qa_prompt,
    build_role_prompt,
)
from factory.state_store import append_run
from factory.task_parser import (
    list_actionable_tasks,
    list_phases,
    load_tasks,
    mark_task_status,
    next_actionable_task,
    next_pending_task,
    pending_in_scope,
    phase_is_complete,
    resolve_scope_tasks,
    tasks_for_story,
)

TASKS_PATH = DOCS_DIR / "TASKS.md"


def should_skip_analyze(
    task: TaskItem,
    *,
    skip_phase: bool = False,
    force_reanalyze: bool = False,
    reuse_if_exists: bool = True,
) -> bool:
    """True = no ejecutar fase Architect."""
    if skip_phase or task.skip_analyze:
        return True
    if force_reanalyze or task.force_analyze:
        return False
    if reuse_if_exists and has_analysis(task.task_id, story=task.story):
        return True
    return False


class SDDOrchestrator:
    """Orquestador SDD: encadena roles vía Cursor SDK."""

    def __init__(
        self,
        *,
        tasks_path: Path = TASKS_PATH,
        dry_run: bool = False,
        progress: ProgressReporter | None = None,
        tier: ModelTier | None = None,
        lean: bool | None = None,
        single_session: bool | None = None,
        auto_release: bool | None = None,
    ) -> None:
        self._tasks_path = tasks_path
        self._dry_run = dry_run
        self._progress = progress or ProgressReporter()
        self._tier = tier
        self._lean = lean
        self._single_session = single_session_enabled() if single_session is None else single_session
        self._auto_release = auto_release_enabled() if auto_release is None else auto_release

    def list_pending(self) -> list[TaskItem]:
        return [t for t in load_tasks(self._tasks_path) if t.status == TaskStatus.PENDING]

    def _get_task(self, task_id: str) -> TaskItem:
        task = next((t for t in load_tasks(self._tasks_path) if t.task_id == task_id), None)
        if task is None:
            raise ValueError(f"Tarea {task_id} no encontrada en TASKS.md")
        if task.status == TaskStatus.COMPLETED:
            raise ValueError(f"Tarea {task_id} ya está completada")
        return task

    def _record_results(self, results: list[RunResult]) -> None:
        if self._dry_run:
            return
        for result in results:
            append_run(result)

    def _resolve_scope(self, scope: QAScope | None) -> tuple[list[TaskItem], str]:
        scope = scope or QAScope()
        tasks = resolve_scope_tasks(
            self._tasks_path,
            phase=scope.phase,
            story_ids=list(scope.story_ids) or None,
            task_ids=list(scope.task_ids) or None,
        )
        return tasks, scope.label()

    def check_gate(
        self,
        scope: QAScope | None = None,
        *,
        require_qa: bool = True,
        require_review: bool = False,
        require_security: bool = False,
        strict: bool = True,
    ) -> GateResult:
        """Evalúa reportes y tareas sin llamar a agentes."""
        scope_tasks, label = self._resolve_scope(scope)
        pending = [t.task_id for t in pending_in_scope(self._tasks_path, scope_tasks)]
        return evaluate_gate(
            require_qa=require_qa,
            require_review=require_review,
            require_security=require_security,
            pending_tasks=pending,
            scope_label=label,
            strict=strict,
        )

    def run_qa(self, scope: QAScope | None = None) -> RunResult:
        scope_tasks, label = self._resolve_scope(scope)
        pending = pending_in_scope(self._tasks_path, scope_tasks)
        if pending:
            ids = ", ".join(t.task_id for t in pending)
            self._progress.error(f"No se puede validar QA: tareas incompletas — {ids}")
            return RunResult(
                role=FactoryRole.QA,
                task_id=None,
                status="blocked",
                agent_id=None,
                summary=f"Tareas incompletas en alcance: {ids}",
                error="Completa las tareas antes de QA",
            )

        self._progress.phase(f"QA — {label}")
        prompt = build_qa_prompt(scope_tasks, label, lean=self._lean)
        return self.run_role(FactoryRole.QA, tier="smart", prompt=prompt)

    def run_release(
        self,
        scope: QAScope | None = None,
        *,
        include_review: bool = True,
        include_security: bool = True,
        strict_gate: bool = True,
    ) -> tuple[list[RunResult], GateResult]:
        """Cierre: QA (+ review/security) y evaluación de gate."""
        results: list[RunResult] = []
        scope_tasks, label = self._resolve_scope(scope)

        pending = pending_in_scope(self._tasks_path, scope_tasks)
        if pending:
            gate = self.check_gate(
                scope,
                require_qa=False,
                require_review=include_review,
                require_security=include_security,
                strict=strict_gate,
            )
            ids = ", ".join(t.task_id for t in pending)
            self._progress.error(f"Release bloqueado: tareas incompletas — {ids}")
            return results, gate

        qa_result = self.run_qa(scope)
        results.append(qa_result)
        if qa_result.status == "error":
            gate = self.check_gate(
                scope,
                require_qa=True,
                require_review=False,
                require_security=False,
                strict=strict_gate,
            )
            return results, gate

        if include_review:
            self._progress.phase(f"Reviewer — {label}")
            prompt = build_closure_prompt(FactoryRole.REVIEWER, label, lean=self._lean)
            results.append(self.run_role(FactoryRole.REVIEWER, tier="smart", prompt=prompt))

        if include_security:
            self._progress.phase(f"Security — {label}")
            prompt = build_closure_prompt(FactoryRole.SECURITY, label, lean=self._lean)
            results.append(self.run_role(FactoryRole.SECURITY, tier="smart", prompt=prompt))

        gate = self.check_gate(
            scope,
            require_qa=True,
            require_review=include_review,
            require_security=include_security,
            strict=strict_gate,
        )
        return results, gate

    def _log_gate(self, gate: GateResult) -> None:
        if gate.passed:
            self._progress.success(f"GATE ABIERTO — {gate.scope_label}")
        else:
            self._progress.error(f"GATE CERRADO — {gate.scope_label}")
            for message in gate.messages:
                self._progress.error(message)

    def _resolve_auto_release_scope(self, task_id: str) -> QAScope | None:
        """Devuelve alcance si debe dispararse auto-validación tras esta tarea."""
        task = next((t for t in load_tasks(self._tasks_path) if t.task_id == task_id), None)
        if task is None:
            return None

        if task.phase and phase_is_complete(self._tasks_path, task.phase):
            return QAScope(phase=task.phase)

        if not task.phase and not self.list_pending():
            return QAScope()

        return None

    def _finalize_dev_batch(self, results: list[RunResult], task_id: str) -> list[RunResult]:
        """Si la fase quedó completa, ejecuta release automático (QA + gate)."""
        if not self._auto_release or self._dry_run:
            return results

        if any(r.status == "error" for r in results):
            return results

        scope = self._resolve_auto_release_scope(task_id)
        if scope is None:
            return results

        _, label = self._resolve_scope(scope)
        include_review = auto_release_include_review()
        include_security = auto_release_include_security()

        self._progress.phase(f"═══ Fase completada — auto-validación: {label} ═══")

        gate_existing = self.check_gate(
            scope,
            require_qa=True,
            require_review=include_review,
            require_security=include_security,
            strict=True,
        )
        if gate_existing.passed:
            self._progress.info("Alcance ya validado; omitiendo agentes de cierre.")
            self._log_gate(gate_existing)
            return results

        release_results, gate = self.run_release(
            scope,
            include_review=include_review,
            include_security=include_security,
            strict_gate=True,
        )
        results.extend(release_results)
        self._log_gate(gate)
        return results

    def list_phases(self) -> list[str]:
        return list_phases(self._tasks_path)

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
                lean=self._lean,
            )
        self._progress.info(f"Prompt listo ({len(prompt)} caracteres)")
        self._progress.info(f"Modelo ({resolved_tier or 'auto'}): {model}")

        results = run_cursor_agent_session(
            [AgentPhase(role=role, task_id=task.task_id if task else None, prompt=prompt, model=model)],
            dry_run=self._dry_run,
            progress=self._progress,
        )
        result = results[0]
        self._record_results([result])
        return result

    def run_analyze_task(self, task_id: str) -> RunResult:
        """Fase 1: analiza requerimiento (modelo smart). No implementa."""
        task = self._get_task(task_id)
        self._progress.phase(f"Análisis de requerimiento — {task_id}")

        prompt = build_analyze_prompt(task, lean=self._lean)
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

    def run_analyze_story(self, story_id: str) -> RunResult:
        """Análisis grupal: una corrida Architect para varias tareas de la misma US."""
        tasks = tasks_for_story(self._tasks_path, story_id)
        if not tasks:
            raise ValueError(f"No hay tareas pendientes/en progreso para {story_id}")

        self._progress.phase(f"Análisis grupal — {story_id} ({len(tasks)} tarea(s))")
        prompt = build_analyze_batch_prompt(story_id, tasks, lean=self._lean)
        result = self.run_role(
            FactoryRole.ARCHITECT,
            extra_instruction=f"Historia {story_id}; tareas: {', '.join(t.task_id for t in tasks)}",
            tier="smart",
            prompt=prompt,
        )

        if self._dry_run or result.status == "error":
            return result

        if story_analysis_path(story_id).exists():
            self._progress.success(f"Análisis grupal en {story_analysis_path(story_id)}")
        elif result.summary:
            save_story_analysis(story_id, result.summary)
            self._progress.success(f"Análisis grupal guardado en {story_analysis_path(story_id)}")

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

        analysis_context = load_analysis(
            task.task_id,
            story=task.story,
            compact=True,
        )
        return self.run_role(
            FactoryRole.DEVELOPER,
            task=task,
            analysis_context=analysis_context,
        )

    def run_developer_task(
        self,
        task_id: str,
        *,
        mark_in_progress: bool = True,
        analysis_context: str | None = None,
        tier: ModelTier | None = None,
        use_analysis: bool = True,
    ) -> RunResult:
        task = self._get_task(task_id)

        if mark_in_progress and not self._dry_run and task.status == TaskStatus.PENDING:
            self._progress.info(f"Marcando {task.task_id} como [~] en TASKS.md")
            mark_task_status(self._tasks_path, task.task_id, TaskStatus.IN_PROGRESS)

        if analysis_context is None and use_analysis:
            analysis_context = load_analysis(task.task_id, story=task.story, compact=True)

        return self.run_role(
            FactoryRole.DEVELOPER,
            task=task,
            analysis_context=analysis_context,
            tier=tier or self._tier,
        )

    def _run_full_task_single_session(self, task: TaskItem) -> list[RunResult]:
        """Análisis + dev en un agente (menos re-lectura del repo)."""
        model = model_for_role(FactoryRole.ARCHITECT, tier="smart")
        analyze_prompt = build_analyze_prompt(task, lean=self._lean)
        dev_prompt = build_dev_followup_prompt(task, lean=self._lean)

        self._progress.info("Modo sesión única: análisis + implementación")
        self._progress.info(f"Prompts: {len(analyze_prompt)} + {len(dev_prompt)} caracteres")

        results = run_cursor_agent_session(
            [
                AgentPhase(
                    FactoryRole.ARCHITECT,
                    task.task_id,
                    analyze_prompt,
                    model,
                ),
                AgentPhase(
                    FactoryRole.DEVELOPER,
                    task.task_id,
                    dev_prompt,
                    model,
                ),
            ],
            dry_run=self._dry_run,
            progress=self._progress,
        )
        self._record_results(results)

        if not self._dry_run and results and results[0].status != "error":
            if not analysis_path(task.task_id).exists() and results[0].summary:
                save_analysis(task.task_id, results[0].summary)

        return self._finalize_dev_batch(results, task.task_id)

    def run_full_task(
        self,
        task_id: str,
        *,
        mark_in_progress: bool = True,
        skip_analyze: bool = False,
        force_analyze: bool = False,
        reuse_analysis: bool = True,
    ) -> list[RunResult]:
        """Un solo comando: Analizar (smart) → Crear + Probar (fast)."""
        task = self._get_task(task_id)
        results: list[RunResult] = []

        if mark_in_progress and not self._dry_run and task.status == TaskStatus.PENDING:
            self._progress.info(f"Marcando {task_id} como [~] en TASKS.md")
            mark_task_status(self._tasks_path, task_id, TaskStatus.IN_PROGRESS)

        do_skip = should_skip_analyze(
            task,
            skip_phase=skip_analyze,
            force_reanalyze=force_analyze,
            reuse_if_exists=reuse_analysis,
        )

        if not do_skip and self._single_session:
            self._progress.phase(f"═══ Sesión única: Análisis + Implementar ({task_id}) ═══")
            results = self._run_full_task_single_session(task)
            return self._finalize_dev_batch(results, task_id)

        if not do_skip:
            self._progress.phase(f"═══ Paso 1/2: Análisis ({task_id}) ═══")
            analyze_result = self.run_analyze_task(task_id)
            results.append(analyze_result)
            if analyze_result.status == "error":
                return results

        self._progress.phase(f"═══ Paso 2/2: Implementar + Probar ({task_id}) ═══")
        dev_result = self.run_developer_task(
            task_id,
            mark_in_progress=False,
            tier="fast",
            use_analysis=not do_skip or has_analysis(task_id, story=task.story),
        )
        results.append(dev_result)
        return self._finalize_dev_batch(results, task_id)

    def run_all(
        self,
        *,
        max_tasks: int | None = None,
        stop_on_error: bool = True,
        reuse_analysis: bool = True,
        skip_analyze: bool = False,
        force_analyze: bool = False,
        batch_analyze_stories: bool = True,
    ) -> list[RunResult]:
        """Ejecuta analyze + implement para todas las tareas pendientes/en progreso."""
        all_results: list[RunResult] = []
        completed_count = 0
        attempted: set[str] = set()
        batched_stories: set[str] = set()

        if batch_analyze_stories and not skip_analyze and not force_analyze:
            self._maybe_batch_analyze_stories(
                all_results,
                attempted_stories=batched_stories,
                reuse_analysis=reuse_analysis,
            )

        while True:
            task = next_actionable_task(self._tasks_path, exclude=attempted)
            if task is None:
                if completed_count == 0 and not attempted:
                    self._progress.info("No hay tareas pendientes ni en progreso.")
                else:
                    self._progress.success(
                        f"Autopilot terminado — {completed_count} tarea(s) procesada(s)."
                    )
                break

            if max_tasks is not None and completed_count >= max_tasks:
                self._progress.info(f"Límite alcanzado (--max {max_tasks}).")
                break

            attempted.add(task.task_id)

            self._progress.phase(
                f"Autopilot [{completed_count + 1}"
                + (f"/{max_tasks}" if max_tasks else "")
                + f"]: {task.task_id} — {task.title}"
            )

            batch = self.run_full_task(
                task.task_id,
                mark_in_progress=True,
                skip_analyze=skip_analyze,
                force_analyze=force_analyze,
                reuse_analysis=reuse_analysis,
            )
            all_results.extend(batch)
            completed_count += 1

            if stop_on_error and any(r.status == "error" for r in batch):
                self._progress.error(f"Detenido en {task.task_id} por error.")
                break

        return all_results

    def _maybe_batch_analyze_stories(
        self,
        results: list[RunResult],
        *,
        attempted_stories: set[str],
        reuse_analysis: bool,
    ) -> None:
        """Pre-analiza historias con 2+ tareas pendientes (1 agente por US)."""
        from factory.spec_parser import parse_story_ids

        story_counts: dict[str, int] = {}
        for task in list_actionable_tasks(self._tasks_path):
            if task.skip_analyze:
                continue
            for story_id in parse_story_ids(task.story):
                story_counts[story_id] = story_counts.get(story_id, 0) + 1

        for story_id, count in story_counts.items():
            if count < 2 or story_id in attempted_stories:
                continue
            if reuse_analysis and story_analysis_path(story_id).exists():
                attempted_stories.add(story_id)
                continue

            pending = tasks_for_story(self._tasks_path, story_id)
            if len(pending) < 2:
                continue

            if all(
                has_analysis(t.task_id, story=t.story) or t.skip_analyze for t in pending
            ):
                attempted_stories.add(story_id)
                continue

            self._progress.phase(f"Análisis grupal previo — {story_id}")
            result = self.run_analyze_story(story_id)
            results.append(result)
            attempted_stories.add(story_id)
            if result.status == "error":
                break

    def run_next_full(
        self,
        *,
        reuse_analysis: bool = True,
        skip_analyze: bool = False,
        force_analyze: bool = False,
    ) -> list[RunResult]:
        """Una sola tarea: la siguiente pendiente o en progreso."""
        task = next_actionable_task(self._tasks_path)
        if task is None:
            return [
                RunResult(
                    role=FactoryRole.DEVELOPER,
                    task_id=None,
                    status="no_tasks",
                    agent_id=None,
                    summary="No hay tareas pendientes ni en progreso.",
                )
            ]
        return self.run_full_task(
            task.task_id,
            skip_analyze=skip_analyze,
            force_analyze=force_analyze,
            reuse_analysis=reuse_analysis,
        )

    def run_pipeline(
        self,
        *,
        max_dev_tasks: int = 1,
        include_qa: bool = True,
        include_review: bool = False,
        include_security: bool = False,
        scope: QAScope | None = None,
    ) -> list[RunResult]:
        """Pipeline automático: Developer (N tareas) → QA → Review → Security."""
        results: list[RunResult] = []

        for _ in range(max_dev_tasks):
            pending_before = self.list_pending()
            if not pending_before:
                break
            batch = self.run_next_full(reuse_analysis=True)
            results.extend(batch)
            if batch and batch[-1].status in {"no_tasks", "error"}:
                break

        scope_tasks, _ = self._resolve_scope(scope)
        dev_done = not pending_in_scope(self._tasks_path, scope_tasks) if scope else not self.list_pending()

        if include_qa and dev_done:
            results.append(self.run_qa(scope))

        if include_review and dev_done:
            _, label = self._resolve_scope(scope)
            prompt = build_closure_prompt(FactoryRole.REVIEWER, label, lean=self._lean)
            results.append(self.run_role(FactoryRole.REVIEWER, tier="smart", prompt=prompt))

        if include_security and dev_done:
            _, label = self._resolve_scope(scope)
            prompt = build_closure_prompt(FactoryRole.SECURITY, label, lean=self._lean)
            results.append(self.run_role(FactoryRole.SECURITY, tier="smart", prompt=prompt))

        return results
