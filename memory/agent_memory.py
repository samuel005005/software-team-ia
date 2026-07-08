from dataclasses import dataclass, field


@dataclass
class AgentMemory:
    """Memoria privada acumulativa de un agente."""

    agent_name: str
    notes: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)

    def add_note(self, note: str) -> None:
        self.notes.append(note)

    def add_decision(self, decision: str) -> None:
        self.decisions.append(decision)
