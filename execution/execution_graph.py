from agents.base_agent import BaseAgent
from agents.agent_result import AgentResult
from execution.execution_node import ExecutionNode
from execution.execution_policy import DefaultExecutionPolicy, ExecutionPolicy


class ExecutionGraph:
    """Grafo de ejecución de agentes. La navegación la decide una ExecutionPolicy."""

    def __init__(self, policy: ExecutionPolicy | None = None) -> None:
        self._nodes: dict[str, ExecutionNode] = {}
        self._start_node: ExecutionNode | None = None
        self._policy = policy or DefaultExecutionPolicy()

    @property
    def policy(self) -> ExecutionPolicy:
        return self._policy

    def add_node(self, node: ExecutionNode) -> ExecutionNode:
        """Registra un nodo en el grafo."""
        if node.id in self._nodes:
            raise ValueError(f"Ya existe un nodo con id '{node.id}'")

        self._nodes[node.id] = node
        if self._start_node is None:
            self._start_node = node
        return node

    def set_start(self, node: ExecutionNode) -> None:
        """Establece el nodo inicial del recorrido."""
        if node.id not in self._nodes:
            raise ValueError(f"El nodo '{node.id}' no está registrado en el grafo")
        self._start_node = node

    def get_node(self, node_id: str) -> ExecutionNode | None:
        return self._nodes.get(node_id)

    def traverse(
        self,
        agent_results: dict[str, AgentResult] | None = None,
    ) -> list[ExecutionNode]:
        """Recorre el grafo desde el nodo inicial usando la policy configurada."""
        if self._start_node is None:
            return []

        order: list[ExecutionNode] = []
        visited: set[str] = set()
        current: ExecutionNode | None = self._start_node
        results = agent_results or {}

        while current is not None:
            if current.id in visited:
                break
            visited.add(current.id)
            order.append(current)

            current = self._policy.choose_next(
                current,
                results.get(current.id),
                self,
            )

        return order

    def get_agents(
        self,
        agent_results: dict[str, AgentResult] | None = None,
    ) -> list[BaseAgent]:
        """Devuelve los agentes en el orden de ejecución del grafo."""
        return [node.agent for node in self.traverse(agent_results)]

    def get_execution_order(
        self,
        agent_results: dict[str, AgentResult] | None = None,
    ) -> list[str]:
        """Devuelve los ids de nodos en orden de ejecución."""
        return [node.id for node in self.traverse(agent_results)]
