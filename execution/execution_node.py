from dataclasses import dataclass, field

from agents.base_agent import BaseAgent


@dataclass
class ExecutionNode:
    """Nodo del grafo de ejecución que encapsula un agente."""

    id: str
    agent: BaseAgent
    next_nodes: list["ExecutionNode"] = field(default_factory=list)

    def connect(self, other: "ExecutionNode") -> "ExecutionNode":
        """Conecta este nodo con el siguiente en el flujo."""
        self.next_nodes.append(other)
        return other
