import os
from pathlib import Path

from factory.config import DEFAULT_CWD, model_for_role
from factory.models import FactoryRole, RunResult
from factory.progress import ProgressReporter


class MissingApiKeyError(RuntimeError):
    """CURSOR_API_KEY no configurada."""


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
    reporter = progress or ProgressReporter(quiet=os.getenv("FACTORY_QUIET") == "1")
    resolved_model = model or os.getenv("FACTORY_MODEL", "composer-2.5")

    if dry_run:
        reporter.phase("Simulación (dry-run)")
        reporter.info(f"Rol: {role.value}")
        if task_id:
            reporter.info(f"Tarea: {task_id}")
        return RunResult(
            role=role,
            task_id=task_id,
            status="dry_run",
            agent_id=None,
            summary=prompt[:500] + ("..." if len(prompt) > 500 else ""),
        )

    api_key = os.getenv("CURSOR_API_KEY")
    if not api_key:
        raise MissingApiKeyError(
            "Define CURSOR_API_KEY para ejecutar agentes. "
            "Obtén la clave en cursor.com → Settings → API."
        )

    try:
        from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions
    except ImportError as exc:
        raise RuntimeError(
            "Instala cursor-sdk: pip install -r requirements-factory.txt"
        ) from exc

    reporter.phase(f"Iniciando agente {role.value}" + (f" — {task_id}" if task_id else ""))
    reporter.info("Verificando API key…")
    reporter.info(f"Modelo: {resolved_model}")
    reporter.info(f"Directorio: {cwd.resolve()}")
    reporter.info("Conectando con Cursor (bridge local — mantén Cursor Desktop abierto)…")

    text_chunks: list[str] = []
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
            reporter.phase("Enviando instrucciones al agente")
            reporter.start_spinner("Esperando respuesta del agente…")

            run = agent.send(prompt)

            for message in run.messages():
                reporter.handle_sdk_message(message)
                if getattr(message, "type", "") == "assistant":
                    for block in getattr(getattr(message, "message", None), "content", ()):
                        text = getattr(block, "text", "")
                        if text:
                            text_chunks.append(text)

            reporter.stop_spinner()
            reporter.flush_assistant()
            reporter.phase("Finalizando ejecución")
            reporter.start_spinner("Esperando resultado final…")
            result = run.wait()
            reporter.stop_spinner()

    except CursorAgentError as exc:
        reporter.stop_spinner()
        reporter.error(f"No se pudo iniciar el agente: {exc.message}")
        if "Connection refused" in str(exc.message) or "ConnectError" in str(exc):
            reporter.error("Abre Cursor Desktop y vuelve a intentar.")
        return RunResult(
            role=role,
            task_id=task_id,
            status="error",
            agent_id=agent_id,
            summary=None,
            error=str(exc.message),
        )
    except Exception as exc:
        reporter.stop_spinner()
        reporter.error(str(exc))
        if "Connection refused" in str(exc) or "ConnectError" in str(exc):
            reporter.error("Abre Cursor Desktop y vuelve a intentar.")
        raise

    summary = result.result if getattr(result, "result", None) else "".join(text_chunks)
    status = str(getattr(result, "status", "completed"))

    if status == "error":
        reporter.error(f"El agente terminó con error (run: {getattr(result, 'id', '?')})")
    elif status in {"finished", "completed"}:
        reporter.success(f"Agente terminó correctamente (run: {getattr(result, 'id', '?')})")
    else:
        reporter.info(f"Estado final: {status}")

    return RunResult(
        role=role,
        task_id=task_id,
        status=status,
        agent_id=agent_id,
        summary=str(summary) if summary else None,
        error=str(summary) if status == "error" else None,
    )
