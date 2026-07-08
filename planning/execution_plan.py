from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionPlan:
    """Plan de ejecución generado por el Planner."""

    nodes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, name: str) -> None:
        self.nodes.append(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": list(self.nodes),
            "metadata": dict(self.metadata),
        }
