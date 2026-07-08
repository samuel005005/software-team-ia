import json
import unittest
from unittest.mock import MagicMock

from agents.agent_registry import AgentDescriptor, AgentRegistry, create_default_registry
from agents.base_agent import BaseAgent
from llm.llm_response import LLMResponse
from parsers.parser_error import ParserError
from parsers.planner_parser import parse


class _StubAgent(BaseAgent):
    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def process(self, state):
        return state


class PlannerParserTestCase(unittest.TestCase):
    def _response(self, content: str) -> LLMResponse:
        return LLMResponse(
            content=content,
            provider="mock",
            model="mock-model-v1",
        )

    def _registry_with_agent(self, agent_id: str) -> AgentRegistry:
        registry = AgentRegistry()
        registry.register(
            AgentDescriptor(
                id=agent_id,
                display_name=agent_id.title(),
                description="Test agent",
                factory=MagicMock(return_value=_StubAgent(agent_id.title())),
            )
        )
        return registry

    def test_parse_valid_registered_agent(self) -> None:
        registry = create_default_registry()
        content = json.dumps(
            {"nodes": ["analyst", "architect", "developer", "qa"]},
            ensure_ascii=False,
        )

        plan = parse(
            self._response(content),
            registry=registry,
            objective="barberia-app",
        )

        self.assertEqual(plan.nodes, ["analyst", "architect", "developer", "qa"])
        self.assertEqual(plan.metadata["objective"], "barberia-app")
        self.assertEqual(plan.metadata["source"], "planner_llm")

    def test_parse_unregistered_agent_raises(self) -> None:
        registry = self._registry_with_agent("analyst")
        content = json.dumps({"nodes": ["analyst", "reviewer"]})

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content), registry=registry)

        self.assertIn("reviewer", str(ctx.exception))

    def test_parse_empty_registry_raises(self) -> None:
        registry = AgentRegistry()
        content = json.dumps({"nodes": ["analyst"]})

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content), registry=registry)

        self.assertIn("No hay agentes registrados", str(ctx.exception))

    def test_parse_invalid_json_raises(self) -> None:
        with self.assertRaises(ParserError):
            parse(
                self._response("not-json"),
                registry=create_default_registry(),
                objective="test",
            )

    def test_parse_missing_nodes_raises(self) -> None:
        content = json.dumps({"flow": ["analyst"]})

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content), registry=create_default_registry())

        self.assertIn("nodes", str(ctx.exception))

    def test_parse_empty_nodes_raises(self) -> None:
        content = json.dumps({"nodes": []})

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content), registry=create_default_registry())

        self.assertIn("vacío", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
