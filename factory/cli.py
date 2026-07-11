import argparse
import sys

from factory.models import FactoryRole, QAScope
from factory.orchestrator import SDDOrchestrator
from factory.progress import ProgressReporter

TIER_CHOICES = ("smart", "fast", "cheap")

# Alias del argumento posicional de `factory run`
_RUN_ALIASES_ONCE = frozenset({"next", "siguiente"})
_RUN_ALIASES_ALL = frozenset({"all", "todo", "todos", "*"})


def _resolve_run_mode(task_id: str | None, *, once_flag: bool) -> tuple[str | None, bool, bool]:
    """Devuelve (task_id, run_once, run_all). Sin ID ni --all → siguiente tarea (once)."""
    if task_id is None:
        return None, True, False

    normalized = task_id.strip().lower()
    if normalized in _RUN_ALIASES_ONCE:
        return None, True, False
    if normalized in _RUN_ALIASES_ALL:
        return None, False, True

    return task_id, once_flag, False


def _add_tier_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--tier",
        choices=TIER_CHOICES,
        default=None,
        help="Tier de modelo: smart (análisis), fast (dev normal), cheap (tareas simples)",
    )


def _add_prompt_mode_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--lean",
        action="store_true",
        default=None,
        help="Prompts por referencia (menos tokens; default si FACTORY_LEAN_PROMPT=1)",
    )
    group.add_argument(
        "--full-prompt",
        action="store_true",
        help="Incluir rule y plantilla completas en el prompt",
    )


def _add_analyze_flags(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--skip-analyze",
        action="store_true",
        help="No ejecutar fase Architect (ir directo a implementar)",
    )
    group.add_argument(
        "--force-analyze",
        action="store_true",
        help="Forzar análisis aunque exista .factory/analysis/",
    )


def _resolve_lean(args) -> bool | None:
    if getattr(args, "full_prompt", False):
        return False
    if getattr(args, "lean", None):
        return True
    return None


def _resolve_single_session(args) -> bool | None:
    if getattr(args, "no_single_session", False):
        return False
    if getattr(args, "single_session", False):
        return True
    return None


def _resolve_auto_release(args) -> bool | None:
    if getattr(args, "no_auto_release", False):
        return False
    return None


def _print_result(result, progress: ProgressReporter) -> None:
    progress.stop_spinner()
    print(f"\n--- {result.role.value} | {result.task_id or '-'} | {result.status} ---")
    if result.agent_id:
        print(f"agent_id: {result.agent_id}")
    if result.summary:
        print(result.summary)
    if result.error:
        print(f"error: {result.error}", file=sys.stderr)


def _add_scope_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--phase",
        default=None,
        help='Fase de TASKS.md (ej. "Fase 1" o "Fase 1 — Fundamentos")',
    )
    parser.add_argument(
        "--story",
        default=None,
        help="Historias US-001,US-002 (coma separada)",
    )
    parser.add_argument(
        "--tasks",
        default=None,
        help="Tareas T-001,T-002 (coma separada)",
    )


def _parse_scope(args) -> QAScope | None:
    phase = getattr(args, "phase", None)
    story_raw = getattr(args, "story", None)
    tasks_raw = getattr(args, "tasks", None)
    if not phase and not story_raw and not tasks_raw:
        return None
    story_ids = tuple(s.strip().upper() for s in story_raw.split(",") if s.strip()) if story_raw else ()
    task_ids = tuple(s.strip().upper() for s in tasks_raw.split(",") if s.strip()) if tasks_raw else ()
    return QAScope(phase=phase, story_ids=story_ids, task_ids=task_ids)


def _print_gate(gate) -> int:
    print(f"\n=== Factory Gate — {gate.scope_label} ===")
    for verdict in gate.verdicts:
        icon = {"pass": "✓", "warn": "!", "fail": "✗", "missing": "?"}.get(verdict.status.value, "?")
        print(f"  [{icon}] {verdict.role}: {verdict.message}")
    if gate.pending_tasks:
        print(f"  Tareas incompletas: {', '.join(gate.pending_tasks)}")
    for message in gate.messages:
        if message not in {v.message for v in gate.verdicts}:
            print(f"  · {message}")
    if gate.passed:
        print("\nGATE ABIERTO — cumple criterios de entrega para este alcance.")
        return 0
    print("\nGATE CERRADO — corrige hallazgos antes de entregar o hacer merge.")
    return 1


def _print_results(results, progress: ProgressReporter) -> int:
    for result in results:
        _print_result(result, progress)
    return 0 if all(r.status != "error" for r in results) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Orquestador SDD — Software Factory con Cursor SDK",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra el prompt sin llamar a la API",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Sin spinner ni progreso detallado",
    )
    _add_prompt_mode_arguments(parser)
    parser.add_argument(
        "--single-session",
        action="store_true",
        default=None,
        help="Análisis + dev en un solo agente (default si FACTORY_SINGLE_SESSION=1)",
    )
    parser.add_argument(
        "--no-single-session",
        action="store_true",
        help="Dos agentes separados (analyze y dev)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("pending", help="Lista tareas pendientes")

    p_next = sub.add_parser("next", help="Ejecuta la siguiente tarea Developer")
    p_next.add_argument(
        "--no-mark-progress",
        action="store_true",
        help="No marcar la tarea como [~] en TASKS.md",
    )
    _add_tier_argument(p_next)

    p_run = sub.add_parser(
        "run",
        help="Analizar + implementar + probar (una tarea, la siguiente, o todas)",
    )
    p_run.add_argument(
        "task_id",
        nargs="?",
        default=None,
        help="T-051, 'next' (siguiente), 'all' (autopilot); vacío = siguiente",
    )
    p_run.add_argument(
        "--once",
        action="store_true",
        help="Solo la siguiente tarea (equivale a 'next')",
    )
    p_run.add_argument(
        "--all",
        action="store_true",
        help="Autopilot: todas las pendientes/en progreso",
    )
    p_run.add_argument(
        "--max",
        type=int,
        default=None,
        metavar="N",
        help="Máximo de tareas en modo automático",
    )
    p_run.add_argument(
        "--continue-on-error",
        action="store_true",
        help="No detener el autopilot si una tarea falla",
    )
    _add_analyze_flags(p_run)
    p_run.add_argument(
        "--no-reuse-analysis",
        action="store_true",
        help="No reutilizar .factory/analysis/ existente (re-analiza si no hay --skip-analyze)",
    )
    p_run.add_argument(
        "--no-batch-analyze",
        action="store_true",
        help="No pre-analizar historias US con varias tareas en un solo agente",
    )
    p_run.add_argument(
        "--no-mark-progress",
        action="store_true",
        help="No marcar la tarea como [~] en TASKS.md",
    )
    p_run.add_argument(
        "--no-auto-release",
        action="store_true",
        help="No ejecutar QA/Review/Security al completar una fase (default: auto)",
    )

    p_analyze = sub.add_parser("analyze", help="Solo Fase 1: analizar requerimiento (smart)")
    p_analyze.add_argument(
        "target",
        help="T-051 o US-003 (análisis grupal de todas las tareas de la historia)",
    )

    p_task = sub.add_parser("task", help="Solo Fase 2+3: implementar + probar")
    p_task.add_argument("task_id", help="Ej. T-044")
    p_task.add_argument(
        "--no-mark-progress",
        action="store_true",
        help="No marcar la tarea como [~] en TASKS.md",
    )
    p_task.add_argument(
        "--no-analysis",
        action="store_true",
        help="No cargar .factory/analysis/ aunque exista",
    )
    _add_tier_argument(p_task)

    p_role = sub.add_parser("role", help="Ejecuta un rol SDD")
    p_role.add_argument(
        "role",
        choices=[r.value for r in FactoryRole],
        help="Rol del equipo",
    )
    p_role.add_argument("--instruction", default=None, help="Texto extra para el agente")
    _add_scope_arguments(p_role)
    _add_tier_argument(p_role)

    p_gate = sub.add_parser("gate", help="Verificar veredictos sin ejecutar agentes")
    _add_scope_arguments(p_gate)
    p_gate.add_argument(
        "--require",
        default="qa",
        help="Reportes requeridos: qa,reviewer,security (coma separada)",
    )
    p_gate.add_argument(
        "--permissive",
        action="store_true",
        help="Acepta CONDICIONAL / RIESGOS (no estricto)",
    )

    p_release = sub.add_parser("release", help="Cierre: QA + Review + Security + gate")
    _add_scope_arguments(p_release)
    p_release.add_argument("--no-review", action="store_true", help="Omitir Reviewer")
    p_release.add_argument("--no-security", action="store_true", help="Omitir Security")
    p_release.add_argument(
        "--permissive",
        action="store_true",
        help="Gate no estricto (permite CONDICIONAL / RIESGOS)",
    )

    p_phases = sub.add_parser("phases", help="Lista fases definidas en TASKS.md")

    p_pipe = sub.add_parser("pipeline", help="Pipeline automático Developer → QA → …")
    p_pipe.add_argument("--max-tasks", type=int, default=1, help="Tareas dev por corrida")
    p_pipe.add_argument("--review", action="store_true", help="Incluir Reviewer")
    p_pipe.add_argument("--security", action="store_true", help="Incluir Security")
    _add_scope_arguments(p_pipe)
    p_pipe.add_argument(
        "--no-mark-progress",
        action="store_true",
        help="No marcar tareas como [~] en TASKS.md",
    )
    _add_tier_argument(p_pipe)

    args = parser.parse_args(argv)
    tier = getattr(args, "tier", None)
    progress = ProgressReporter(quiet=args.quiet)
    orchestrator = SDDOrchestrator(
        dry_run=args.dry_run,
        progress=progress,
        tier=tier,
        lean=_resolve_lean(args),
        single_session=_resolve_single_session(args),
        auto_release=_resolve_auto_release(args),
    )

    try:
        if args.command == "pending":
            pending = orchestrator.list_pending()
            if not pending:
                print("No hay tareas pendientes.")
                return 0
            for task in pending:
                flags = []
                if task.skip_analyze:
                    flags.append("skip-analyze")
                if task.force_analyze:
                    flags.append("force-analyze")
                suffix = f" [{', '.join(flags)}]" if flags else ""
                print(f"{task.task_id} | {task.title} | {task.story or '-'}{suffix}")
            return 0

        if args.command == "phases":
            phases = orchestrator.list_phases()
            if not phases:
                print("No hay fases (encabezados ## Fase …) en TASKS.md")
                return 0
            for phase in phases:
                print(phase)
            return 0

        if args.command == "gate":
            scope = _parse_scope(args)
            required = {r.strip().lower() for r in args.require.split(",") if r.strip()}
            gate = orchestrator.check_gate(
                scope,
                require_qa="qa" in required,
                require_review="reviewer" in required or "review" in required,
                require_security="security" in required,
                strict=not args.permissive,
            )
            return _print_gate(gate)

        if args.command == "release":
            scope = _parse_scope(args)
            results, gate = orchestrator.run_release(
                scope,
                include_review=not args.no_review,
                include_security=not args.no_security,
                strict_gate=not args.permissive,
            )
            code = _print_results(results, progress)
            gate_code = _print_gate(gate)
            return max(code, gate_code)

        if args.command == "run":
            task_id, run_once, run_all = _resolve_run_mode(
                args.task_id,
                once_flag=args.once,
            )
            if args.all:
                run_all = True
                run_once = False

            analyze_kwargs = {
                "skip_analyze": args.skip_analyze,
                "force_analyze": args.force_analyze,
                "reuse_analysis": not args.no_reuse_analysis,
            }

            if task_id:
                results = orchestrator.run_full_task(
                    task_id,
                    mark_in_progress=not args.no_mark_progress,
                    **analyze_kwargs,
                )
            elif run_once:
                results = orchestrator.run_next_full(**analyze_kwargs)
            else:
                results = orchestrator.run_all(
                    max_tasks=args.max,
                    stop_on_error=not args.continue_on_error,
                    batch_analyze_stories=not args.no_batch_analyze,
                    **analyze_kwargs,
                )
            return _print_results(results, progress)

        if args.command == "analyze":
            target = args.target.strip()
            if target.upper().startswith("US-"):
                result = orchestrator.run_analyze_story(target.upper())
            else:
                result = orchestrator.run_analyze_task(target)
            _print_result(result, progress)
            return 0 if result.status != "error" else 1

        if args.command == "next":
            result = orchestrator.run_developer_next(
                mark_in_progress=not args.no_mark_progress,
            )
            _print_result(result, progress)
            return 0 if result.status not in {"error", "no_tasks"} else 1

        if args.command == "task":
            result = orchestrator.run_developer_task(
                args.task_id,
                mark_in_progress=not args.no_mark_progress,
                use_analysis=not args.no_analysis,
            )
            _print_result(result, progress)
            return 0 if result.status != "error" else 1

        if args.command == "role":
            role = FactoryRole(args.role)
            scope = _parse_scope(args)
            if role == FactoryRole.QA and scope is not None:
                result = orchestrator.run_qa(scope)
            elif role == FactoryRole.QA:
                result = orchestrator.run_qa()
            else:
                result = orchestrator.run_role(role, extra_instruction=args.instruction)
            _print_result(result, progress)
            return 0 if result.status not in {"error", "blocked"} else 1

        if args.command == "pipeline":
            results = orchestrator.run_pipeline(
                max_dev_tasks=args.max_tasks,
                include_review=args.review,
                include_security=args.security,
                scope=_parse_scope(args),
            )
            return _print_results(results, progress)

    except Exception as exc:
        progress.stop_spinner()
        progress.error(str(exc))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
