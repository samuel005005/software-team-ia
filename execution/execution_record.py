from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class ExecutionStatus:
    """Constantes de estado para ejecuciones de agentes."""

    RUNNING: str = "RUNNING"
    SUCCESS: str = "SUCCESS"
    FAILED: str = "FAILED"

    # Estados reservados para futuras versiones
    RETRY: str = "RETRY"
    TIMEOUT: str = "TIMEOUT"
    CANCELLED: str = "CANCELLED"
    SKIPPED: str = "SKIPPED"


@dataclass
class ExecutionRecord:
    """Registro de una ejecución individual de un agente."""

    agent_name: str
    started_at: datetime
    finished_at: datetime | None = None
    input_summary: str = ""
    output_summary: str = ""
    status: str = ExecutionStatus.RUNNING
    errors: list[str] = field(default_factory=list)
    duration_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.finished_at is not None and self.duration_ms is None:
            self.duration_ms = int(
                (self.finished_at - self.started_at).total_seconds() * 1000
            )
