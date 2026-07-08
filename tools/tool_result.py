from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """Resultado estructurado de la ejecución de una herramienta."""

    success: bool
    output: Any
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def success_result(
        cls,
        output: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> "ToolResult":
        return cls(
            success=True,
            output=output,
            metadata=metadata or {},
        )

    @classmethod
    def failure_result(
        cls,
        error: str,
        *,
        output: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> "ToolResult":
        return cls(
            success=False,
            output=output,
            error=error,
            metadata=metadata or {},
        )
