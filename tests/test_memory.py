import unittest

from memory.agent_memory import AgentMemory
from memory.memory_store import MemoryStore


class MemoryStoreTestCase(unittest.TestCase):
    def test_get_creates_memory_if_not_exists(self) -> None:
        store = MemoryStore()

        memory = store.get("Business Analyst")

        self.assertIsInstance(memory, AgentMemory)
        self.assertEqual(memory.agent_name, "Business Analyst")
        self.assertEqual(memory.notes, [])
        self.assertEqual(memory.decisions, [])

    def test_get_returns_same_instance(self) -> None:
        store = MemoryStore()

        first = store.get("Flutter Developer")
        second = store.get("Flutter Developer")

        self.assertIs(first, second)

    def test_agent_memory_add_note_and_decision(self) -> None:
        memory = AgentMemory(agent_name="QA Engineer")
        memory.add_note("Validación completada")
        memory.add_decision("Aprobar si existen 3 artefactos mínimos")

        self.assertEqual(memory.notes, ["Validación completada"])
        self.assertEqual(memory.decisions, ["Aprobar si existen 3 artefactos mínimos"])

    def test_get_all_returns_all_memories(self) -> None:
        store = MemoryStore()
        store.get("Business Analyst")
        store.get("Software Architect")

        all_memories = store.get_all()

        self.assertEqual(len(all_memories), 2)
        self.assertIn("Business Analyst", all_memories)
        self.assertIn("Software Architect", all_memories)


if __name__ == "__main__":
    unittest.main()
