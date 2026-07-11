import os
from dataclasses import dataclass
from pathlib import Path

from factory.config import DEFAULT_CWD, model_for_role
from factory.models import FactoryRole, RunResult
from factory.progress import ProgressReporter


class MissingApiKeyError(RuntimeError):
    """CURSOR_API_KEY no configurada."""


@dataclass(frozen=True)
class AgentPhase:
    """Una fase dentro de una sesión multi-prompt."""

    role: FactoryRole
    task_id: str | None
    prompt: str
    model: str | None = None


def _finalize_run(
    run,
    *,
    role: FactoryRole,
    task_id: str | None,
    agent_id: str | None,
    text_chunks: list[str],
) -> RunResult:
    result = run.wait()
    summary = result.result if getattr(result, "result", None) else "".join(text_chunks)
    status = str(getattr(result, "status", "completed"))
    return RunResult(
        role=role,
        task_id=task_id,
        status=status,
        agent_id=agent_id,
        summary=str(summary) if summary else None,
        error=str(summary) if status == "error" else None,
    )


def run_cursor_agent(
    prompt: str,
    *,
    role: FactoryRole,
    task_id: str | None,
    cwd: Path = DEFAULT_CWD,
    model: str | None = None,
    dry_run: bool = False,
    progress: ProgressReporter | None = None,
) -> RunResult:
    return run_cursor_agent_session(
        [
            AgentPhase(role=role, task_id=task_id, prompt=prompt, model=model),
        ],
        cwd=cwd,
        dry_run=dry_run,
        progress=progress,
    )[0]


def run_cursor_agent_session(
    phases: list[AgentPhase],
    *,
    cwd: Path = DEFAULT_CWD,
    dry_run: bool = False,
    progress: ProgressReporter | None = None,
) -> list[RunResult]:
    """Ejecuta varios prompts en un solo agente (reutiliza contexto)."""
    if not phases:
        return []

    reporter = progress or ProgressReporter(quiet=os.getenv("FACTORY_QUIET") == "1")

    if dry_run:
        reporter.phase("Simulación (dry-run)")
        results: list[RunResult] = []
        for index, phase in enumerate(phases, start=1):
            reporter.info(f"Fase {index}/{len(phases)}: {phase.role.value}")
            if phase.task_id:
                reporter.info(f"Tarea: {phase.task_id}")
            results.append(
                RunResult(
                    role=phase.role,
                    task_id=phase.task_id,
                    status="dry_run",
                    agent_id=None,
                    summary=phase.prompt[:500] + ("..." if len(phase.prompt) > 500 else ""),
                )
            )
        return results

    api_key = os.getenv("CURSOR_API_KEY")
    if not api_key:
        raise MissingApiKeyError(
            "Define CURSOR_API_KEY para ejecutar agentes. "
            "Añádela en `.env` (raíz del repo) o exporta la variable. "
            "Obtén la clave en cursor.com → Settings → API."
        )

    try:
        from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions
    except ImportError as exc:
        raise RuntimeError(
            "Falta cursor-sdk. Configura el entorno:\n"
            "  python3 -m venv .venv\n"
            "  source .venv/bin/activate\n"
            "  pip install -r requirements-factory.txt\n"
            "Luego: python -m factory run"
        ) from exc

    first = phases[0]
    resolved_model = first.model or model_for_role(first.role)

    reporter.phase(
        f"Sesión agente ({len(phases)} fase(s)) — {first.role.value}"
        + (f" — {first.task_id}" if first.task_id else "")
    )
    reporter.info(f"Modelo sesión: {resolved_model}")
    reporter.info(f"Directorio: {cwd.resolve()}")

    results: list[RunResult] = []
    agent_id: str | None = None

    try:
        with Agent.create(
            AgentOptions(
                api_key=api_key,
                model=resolved_model,
                local=LocalAgentOptions(cwd=str(cwd.resolve())),
            ),
        ) as agent:
            agent_id = agent.agent_id
            reporter.success(f"Agente creado (id: {agent_id})")

            for index, phase in enumerate(phases, start=1):
                reporter.phase(
                    f"Fase {index}/{len(phases)}: {phase.role.value}"
                    + (f" — {phase.task_id}" if phase.task_id else "")
                )
                reporter.info(f"Prompt ({len(phase.prompt)} caracteres)")
                reporter.start_spinner("Esperando respuesta del agente…")

                run = agent.send(phase.prompt)
                text_chunks: list[str] = []

                for message in run.messages():
                    reporter.handle_sdk_message(message)
                    if getattr(message, "type", "") == "assistant":
                        for block in getattr(getattr(message, "message", None), "content", ()):
                            text = getattr(block, "text", "")
                            if text:
                                text_chunks.append(text)

                reporter.stop_spinner()
                reporter.flush_assistant()
                reporter.start_spinner("Esperando resultado final…")
                phase_result = _finalize_run(
                    run,
                    role=phase.role,
                    task_id=phase.task_id,
                    agent_id=agent_id,
                    text_chunks=text_chunks,
                )
                reporter.stop_spinner()
                results.append(phase_result)

                if phase_result.status == "error":
                    reporter.error(f"Fase {index} terminó con error.")
                    break

    except CursorAgentError as exc:
        reporter.stop_spinner()
        reporter.error(f"No se pudo iniciar el agente: {exc.message}")
        if "Connection refused" in str(exc.message) or "ConnectError" in str(exc):
            reporter.error("Abre Cursor Desktop y vuelve a intentar.")
        return [
            RunResult(
                role=phases[0].role,
                task_id=phases[0].task_id,
                status="error",
                agent_id=agent_id,
                summary=None,
                error=str(exc.message),
            )
        ]
    except Exception as exc:
        reporter.stop_spinner()
        reporter.error(str(exc))
        if "Connection refused" in str(exc) or "ConnectError" in str(exc):
            reporter.error("Abre Cursor Desktop y vuelve a intentar.")
        raise

    last = results[-1] if results else None
    if last and last.status in {"finished", "completed"}:
        reporter.success("Sesión de agente terminada correctamente.")
    elif last and last.status == "error":
        reporter.error("Sesión de agente terminó con error.")

    return results
