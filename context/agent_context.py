from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    """Vista filtrada del estado del proyecto para un agente específico."""

    agent_name: str
    role: str
    inputs: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
