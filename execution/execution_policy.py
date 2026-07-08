from typing import TYPE_CHECKING

from agents.agent_result import AgentResult
from execution.execution_node import ExecutionNode

if TYPE_CHECKING:
    from execution.execution_graph import ExecutionGraph


class ExecutionPolicy:
    """Define las reglas de navegación sobre un ExecutionGraph."""

    def choose_next(
        self,
        current_node: ExecutionNode,
        agent_result: AgentResult | None,
        execution_graph: "ExecutionGraph",
    ) -> ExecutionNode | None:
        raise NotImplementedError


class DefaultExecutionPolicy(ExecutionPolicy):
    """Política lineal por defecto: avanza al primer nodo siguiente."""

    def choose_next(
        self,
        current_node: ExecutionNode,
        agent_result: AgentResult | None,
        execution_graph: "ExecutionGraph",
    ) -> ExecutionNode | None:
        if not current_node.next_nodes:
            return None
        return current_node.next_nodes[0]
