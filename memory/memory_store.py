from memory.agent_memory import AgentMemory


class MemoryStore:
    """Almacén de memorias privadas por agente."""

    def __init__(self) -> None:
        self._memories: dict[str, AgentMemory] = {}

    def get(self, agent_name: str) -> AgentMemory:
        if agent_name not in self._memories:
            self._memories[agent_name] = AgentMemory(agent_name=agent_name)
        return self._memories[agent_name]

    def get_all(self) -> dict[str, AgentMemory]:
        return dict(self._memories)
