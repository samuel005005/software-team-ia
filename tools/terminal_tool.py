import subprocess
from typing import Any

from tools.base_tool import BaseTool


class TerminalTool(BaseTool):
    """Herramienta para ejecutar comandos del sistema usando subprocess."""

    @property
    def name(self) -> str:
        return "terminal"

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        if action == "run_command":
            return self.run_command(params["command"])
        return {
            "success": False,
            "output": "",
            "error": f"Acción no soportada: {action}",
            "return_code": -1,
            "logs": [f"[terminal] Acción no soportada: {action}"],
        }

    def run_command(self, command: str) -> dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "logs": [
                    f"[terminal] Comando ejecutado: {command}",
                    f"[terminal] Código de retorno: {result.returncode}",
                ],
            }
        except Exception as exc:
            return {
                "success": False,
                "output": "",
                "error": str(exc),
                "return_code": -1,
                "logs": [
                    f"[terminal] Error al ejecutar comando: {command}",
                    f"[terminal] Excepción: {exc}",
                ],
            }
