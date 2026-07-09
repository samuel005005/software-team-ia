import argparse
import sys

from factory.models import FactoryRole
from factory.orchestrator import SDDOrchestrator
from factory.progress import ProgressReporter

TIER_CHOICES = ("smart", "fast", "cheap")


def _add_tier_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--tier",
        choices=TIER_CHOICES,
        default=None,
        help="Tier de modelo: smart (análisis), fast (dev normal), cheap (tareas simples)",
    )


def _print_result(result, progress: ProgressReporter) -> None:
    progress.stop_spinner()
    print(f"\n--- {result.role.value} | {result.task_id or '-'} | {result.status} ---")
    if result.agent_id:
        print(f"agent_id: {result.agent_id}")
    if result.summary:
        print(result.summary)
    if result.error:
        print(f"error: {result.error}", file=sys.stderr)


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
        help="Todo en uno: analizar (smart) + implementar + probar (fast)",
    )
    p_run.add_argument("task_id", help="Ej. T-051")
    p_run.add_argument(
        "--skip-analyze",
        action="store_true",
        help="Saltar análisis si ya existe .factory/analysis/T-XXX.md",
    )
    p_run.add_argument(
        "--no-mark-progress",
        action="store_true",
        help="No marcar la tarea como [~] en TASKS.md",
    )

    p_analyze = sub.add_parser("analyze", help="Solo Fase 1: analizar requerimiento (smart)")
    p_analyze.add_argument("task_id", help="Ej. T-051")

    p_task = sub.add_parser("task", help="Solo Fase 2+3: implementar + probar")
    p_task.add_argument("task_id", help="Ej. T-044")
    p_task.add_argument(
        "--no-mark-progress",
        action="store_true",
        help="No marcar la tarea como [~] en TASKS.md",
    )
    p_task.add_argument(
        "--use-analysis",
        action="store_true",
        help="Usar .factory/analysis/T-XXX.md si existe",
    )
    _add_tier_argument(p_task)

    p_role = sub.add_parser("role", help="Ejecuta un rol SDD")
    p_role.add_argument(
        "role",
        choices=[r.value for r in FactoryRole],
        help="Rol del equipo",
    )
    p_role.add_argument("--instruction", default=None, help="Texto extra para el agente")
    _add_tier_argument(p_role)

    p_pipe = sub.add_parser("pipeline", help="Pipeline automático Developer → QA → …")
    p_pipe.add_argument("--max-tasks", type=int, default=1, help="Tareas dev por corrida")
    p_pipe.add_argument("--review", action="store_true", help="Incluir Reviewer")
    p_pipe.add_argument("--security", action="store_true", help="Incluir Security")
    p_pipe.add_argument(
        "--no-mark-progress",
        action="store_true",
        help="No marcar tareas como [~] en TASKS.md",
    )
    _add_tier_argument(p_pipe)

    args = parser.parse_args(argv)
    tier = getattr(args, "tier", None)
    progress = ProgressReporter(quiet=args.quiet)
    orchestrator = SDDOrchestrator(dry_run=args.dry_run, progress=progress, tier=tier)

    try:
        if args.command == "pending":
            pending = orchestrator.list_pending()
            if not pending:
                print("No hay tareas pendientes.")
                return 0
            for task in pending:
                print(f"{task.task_id} | {task.title} | {task.story or '-'}")
            return 0

        if args.command == "run":
            results = orchestrator.run_full_task(
                args.task_id,
                mark_in_progress=not args.no_mark_progress,
                skip_analyze=args.skip_analyze,
            )
            return _print_results(results, progress)

        if args.command == "analyze":
            result = orchestrator.run_analyze_task(args.task_id)
            _print_result(result, progress)
            return 0 if result.status != "error" else 1

        if args.command == "next":
            result = orchestrator.run_developer_next(
                mark_in_progress=not args.no_mark_progress,
            )
            _print_result(result, progress)
            return 0 if result.status not in {"error", "no_tasks"} else 1

        if args.command == "task":
            analysis_context = None
            if args.use_analysis:
                from factory.analysis_store import load_analysis

                analysis_context = load_analysis(args.task_id)
            result = orchestrator.run_developer_task(
                args.task_id,
                mark_in_progress=not args.no_mark_progress,
                analysis_context=analysis_context,
            )
            _print_result(result, progress)
            return 0 if result.status != "error" else 1

        if args.command == "role":
            role = FactoryRole(args.role)
            result = orchestrator.run_role(role, extra_instruction=args.instruction)
            _print_result(result, progress)
            return 0 if result.status != "error" else 1

        if args.command == "pipeline":
            results = orchestrator.run_pipeline(
                max_dev_tasks=args.max_tasks,
                include_review=args.review,
                include_security=args.security,
            )
            return _print_results(results, progress)

    except Exception as exc:
        progress.stop_spinner()
        progress.error(str(exc))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
