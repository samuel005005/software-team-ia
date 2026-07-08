from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AgentResult:
    """Resultado estructurado producido por un agente."""

    agent_name: str
    success: bool
    output: str
    confidence: float = 1.0
    warnings: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.success and self.confidence == 1.0:
            self.confidence = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def success_result(
        cls,
        agent_name: str,
        output: str,
        *,
        confidence: float = 1.0,
        warnings: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "AgentResult":
        return cls(
            agent_name=agent_name,
            success=True,
            output=output,
            confidence=confidence,
            warnings=warnings or [],
            metadata=metadata or {},
        )

    @classmethod
    def failure_result(
        cls,
        agent_name: str,
        output: str,
        *,
        issues: list[str] | None = None,
        warnings: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "AgentResult":
        return cls(
            agent_name=agent_name,
            success=False,
            output=output,
            confidence=0.0,
            warnings=warnings or [],
            issues=issues or [],
            metadata=metadata or {},
        )
