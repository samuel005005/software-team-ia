"""Salida de progreso en terminal para ejecuciones del orquestador."""

from __future__ import annotations

import sys
import threading
from datetime import datetime
from typing import Any


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _shorten(text: str, limit: int = 120) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def _rel_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    for marker in ("software-team-ai/", "projects/"):
        if marker in normalized:
            return normalized.split(marker, 1)[1]
    return path


def describe_tool(name: str, args: Any = None) -> str:
    """Traduce una tool call del agente a texto legible."""
    if name.startswith("read:"):
        return f"Leyendo: {_rel_path(name[5:].strip())}"
    if name.startswith("write:") or name.startswith("edit:"):
        return f"Editando: {_rel_path(name.split(':', 1)[1].strip())}"
    if name.startswith("shell:"):
        return f"Terminal: {_shorten(name[6:].strip(), 80)}"

    labels = {
        "read_file": "Leyendo",
        "Read": "Leyendo",
        "write": "Escribiendo",
        "Write": "Escribiendo",
        "search_replace": "Editando",
        "StrReplace": "Editando",
        "grep": "Buscando",
        "Grep": "Buscando",
        "glob_file_search": "Buscando archivos",
        "Glob": "Buscando archivos",
        "glob": "Buscando archivos",
        "run_terminal_cmd": "Terminal",
        "Shell": "Terminal",
        "list_dir": "Listando",
        "delete_file": "Eliminando",
    }

    label = labels.get(name, name)
    if not isinstance(args, dict):
        return label

    path = args.get("path") or args.get("target_file") or args.get("file")
    if path:
        return f"{label}: {_rel_path(str(path))}"

    pattern = args.get("pattern") or args.get("glob_pattern")
    if pattern:
        return f"{label}: {pattern}"

    command = args.get("command")
    if command:
        return f"{label}: {_shorten(str(command), 80)}"

    return label


class ProgressReporter:
    """Muestra fases, spinner y acciones del agente en la terminal."""

    def __init__(self, *, quiet: bool = False) -> None:
        self.quiet = quiet
        self._spinner_stop = threading.Event()
        self._spinner_thread: threading.Thread | None = None
        self._spinner_message = ""
        self._assistant_buffer = ""
        self._seen_tool_calls: set[str] = set()
        self._completed_tool_calls: set[str] = set()

    def phase(self, message: str) -> None:
        if self.quiet:
            return
        self.stop_spinner()
        print(f"\n[{_timestamp()}] ▶ {message}", flush=True)

    def info(self, message: str) -> None:
        if self.quiet:
            return
        self.stop_spinner()
        print(f"[{_timestamp()}]   → {message}", flush=True)

    def success(self, message: str) -> None:
        if self.quiet:
            return
        self.stop_spinner()
        print(f"[{_timestamp()}] ✓ {message}", flush=True)

    def error(self, message: str) -> None:
        self.stop_spinner()
        print(f"[{_timestamp()}] ✗ {message}", file=sys.stderr, flush=True)

    def start_spinner(self, message: str) -> None:
        if self.quiet:
            return
        self._spinner_message = message
        if self._spinner_thread is not None and self._spinner_thread.is_alive():
            return
        self._spinner_stop.clear()
        self._spinner_thread = threading.Thread(
            target=self._spin,
            daemon=True,
        )
        self._spinner_thread.start()

    def stop_spinner(self) -> None:
        if self._spinner_thread is None:
            return
        self._spinner_stop.set()
        self._spinner_thread.join(timeout=1)
        self._spinner_thread = None
        if not self.quiet:
            sys.stdout.write("\r" + " " * 100 + "\r")
            sys.stdout.flush()

    def flush_assistant(self) -> None:
        """Muestra el texto acumulado del agente (una sola línea)."""
        if self.quiet or not self._assistant_buffer.strip():
            self._assistant_buffer = ""
            return
        self.stop_spinner()
        print(
            f"[{_timestamp()}]   💬 {_shorten(self._assistant_buffer.strip(), 160)}",
            flush=True,
        )
        self._assistant_buffer = ""

    def _spin(self) -> None:
        frames = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
        index = 0
        while not self._spinner_stop.wait(0.12):
            frame = frames[index % len(frames)]
            line = f"\r[{_timestamp()}] {frame} {self._spinner_message}"
            sys.stdout.write(line[:100].ljust(100))
            sys.stdout.flush()
            index += 1

    def handle_sdk_message(self, message: Any) -> None:
        if self.quiet:
            return

        msg_type = getattr(message, "type", None) or (
            message.get("type") if isinstance(message, dict) else None
        )

        if msg_type == "tool_call":
            self.flush_assistant()
            name = getattr(message, "name", "") or ""
            status = getattr(message, "status", "") or ""
            call_id = getattr(message, "call_id", None) or name
            args = getattr(message, "args", None)
            detail = describe_tool(name, args)

            if status == "running" and call_id not in self._seen_tool_calls:
                self._seen_tool_calls.add(call_id)
                self.info(detail)
            elif status == "completed" and call_id not in self._completed_tool_calls:
                self._completed_tool_calls.add(call_id)
            elif status == "error":
                self.error(f"Falló: {detail}")
            return

        if msg_type == "status":
            text = getattr(message, "message", "") or ""
            if text:
                self.info(text)
            return

        if msg_type == "task":
            text = getattr(message, "text", "") or ""
            if text:
                self.info(f"Tarea: {_shorten(text)}")
            return

        if msg_type == "thinking":
            self.start_spinner("Agente pensando…")
            return

        if msg_type == "assistant":
            content = getattr(getattr(message, "message", None), "content", ())
            for block in content:
                text = getattr(block, "text", "")
                if text:
                    self._assistant_buffer += text
            preview = _shorten(self._assistant_buffer.strip(), 70) or "Agente escribiendo…"
            self.start_spinner(f"💬 {preview}")
            return

    def handle_sdk_message_json(self, raw: Any) -> None:
        if isinstance(raw, dict):
            msg_type = raw.get("type")
            if msg_type == "tool_call":
                self.handle_sdk_message(
                    type(
                        "ToolMsg",
                        (),
                        {
                            "type": "tool_call",
                            "name": raw.get("name", ""),
                            "status": raw.get("status", "running"),
                            "args": raw.get("args"),
                            "call_id": raw.get("call_id"),
                        },
                    )()
                )
            return
        self.handle_sdk_message(raw)
