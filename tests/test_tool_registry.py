import unittest
from unittest.mock import MagicMock

from tools.tool import Tool
from tools.tool_descriptor import ToolDescriptor
from tools.tool_registry import ToolRegistry, create_default_tool_registry
from tools.tool_result import ToolResult


class _StubTool(Tool):
    def __init__(self, name: str, description: str = "Herramienta de prueba") -> None:
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output=kwargs)


class ToolRegistryTestCase(unittest.TestCase):
    def test_register_and_get_tool_descriptor(self) -> None:
        registry = ToolRegistry()
        descriptor = ToolDescriptor(
            name="echo",
            description="Repite parámetros",
            capabilities=["echo"],
            tool_factory=lambda: _StubTool("echo"),
        )

        registry.register(descriptor)

        self.assertIs(registry.get("echo"), descriptor)
        self.assertTrue(registry.exists("echo"))

    def test_list_tools_preserves_registration_order(self) -> None:
        registry = ToolRegistry()
        registry.register(
            ToolDescriptor(
                name="alpha",
                description="Primera",
                tool_factory=lambda: _StubTool("alpha"),
            )
        )
        registry.register(
            ToolDescriptor(
                name="beta",
                description="Segunda",
                tool_factory=lambda: _StubTool("beta"),
            )
        )

        self.assertEqual(registry.list_names(), ["alpha", "beta"])
        self.assertEqual(len(registry.list_tools()), 2)

    def test_duplicate_registration_raises(self) -> None:
        registry = ToolRegistry()
        descriptor = ToolDescriptor(
            name="echo",
            description="Repite parámetros",
            tool_factory=lambda: _StubTool("echo"),
        )

        registry.register(descriptor)

        with self.assertRaises(ValueError) as ctx:
            registry.register(descriptor)

        self.assertIn("echo", str(ctx.exception))

    def test_create_tool_uses_factory(self) -> None:
        factory = MagicMock(return_value=_StubTool("echo"))
        registry = ToolRegistry()
        registry.register(
            ToolDescriptor(
                name="echo",
                description="Repite parámetros",
                tool_factory=factory,
            )
        )

        tool = registry.create_tool("echo")

        self.assertIsInstance(tool, Tool)
        factory.assert_called_once_with()

    def test_create_tool_raises_for_unknown_name(self) -> None:
        registry = ToolRegistry()

        with self.assertRaises(KeyError) as ctx:
            registry.create_tool("missing")

        self.assertIn("missing", str(ctx.exception))

    def test_default_registry_registers_filesystem_tools(self) -> None:
        registry = create_default_tool_registry()

        self.assertEqual(len(registry.list_tools()), 6)
        self.assertTrue(registry.exists("create_file"))
        self.assertTrue(registry.exists("read_file"))


if __name__ == "__main__":
    unittest.main()
