import unittest
from unittest.mock import MagicMock

from agents.agent_registry import AgentDescriptor, AgentRegistry, create_default_registry
from agents.base_agent import BaseAgent
from llm.mock_provider import MockLLMProvider
from memory.memory_store import MemoryStore


class _StubAgent(BaseAgent):
    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def process(self, state):
        return state


class AgentRegistryTestCase(unittest.TestCase):
    def test_register_and_get_agent(self) -> None:
        registry = AgentRegistry()
        descriptor = AgentDescriptor(
            id="analyst",
            display_name="Business Analyst",
            description="Genera historias de usuario",
            capabilities=["user_stories"],
            factory=lambda llm, memory: _StubAgent("Business Analyst"),
        )

        registry.register(descriptor)

        self.assertIs(registry.get("analyst"), descriptor)

    def test_list_agents_preserves_registration_order(self) -> None:
        registry = create_default_registry()

        self.assertEqual(
            registry.list_ids(),
            ["analyst", "architect", "developer", "qa"],
        )
        self.assertEqual(len(registry.list_agents()), 4)

    def test_list_capabilities(self) -> None:
        registry = create_default_registry()

        capabilities = registry.list_capabilities()

        self.assertIn("user_stories", capabilities["analyst"])
        self.assertIn("software_design_document", capabilities["architect"])
        self.assertIn("tasks", capabilities["developer"])
        self.assertIn("qa_report", capabilities["qa"])

    def test_duplicate_registration_raises(self) -> None:
        registry = AgentRegistry()
        factory = lambda llm, memory: _StubAgent("test")
        descriptor = AgentDescriptor(
            id="analyst",
            display_name="Analyst",
            description="Test",
            factory=factory,
        )

        registry.register(descriptor)

        with self.assertRaises(ValueError) as ctx:
            registry.register(descriptor)

        self.assertIn("analyst", str(ctx.exception))

    def test_create_agent_uses_factory(self) -> None:
        registry = AgentRegistry()
        factory = MagicMock(return_value=_StubAgent("Business Analyst"))
        registry.register(
            AgentDescriptor(
                id="analyst",
                display_name="Business Analyst",
                description="Genera historias de usuario",
                capabilities=["user_stories"],
                factory=factory,
            )
        )

        llm_provider = MockLLMProvider()
        memory_store = MemoryStore()
        agent = registry.create_agent("analyst", llm_provider, memory_store)

        self.assertIsInstance(agent, BaseAgent)
        factory.assert_called_once_with(llm_provider, memory_store)

    def test_build_agents_returns_all_registered_agents(self) -> None:
        registry = create_default_registry()
        agents = registry.build_agents(MockLLMProvider(), MemoryStore())

        self.assertEqual(set(agents.keys()), {"analyst", "architect", "developer", "qa"})
        self.assertTrue(all(isinstance(agent, BaseAgent) for agent in agents.values()))


if __name__ == "__main__":
    unittest.main()
