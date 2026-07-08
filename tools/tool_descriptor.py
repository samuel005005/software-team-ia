from collections.abc import Callable
from dataclasses import dataclass, field

from tools.tool import Tool

ToolFactory = Callable[[], Tool]


@dataclass
class ToolDescriptor:
    """Metadatos y factory de una herramienta registrada."""

    name: str
    description: str
    tool_factory: ToolFactory = field(repr=False)
    capabilities: list[str] = field(default_factory=list)
