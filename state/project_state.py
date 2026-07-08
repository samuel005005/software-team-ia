from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from actions.base_action import BaseAction

from execution.execution_history import ExecutionHistory


@dataclass
class ProjectState:
    """Estado completo de un proyecto generado por los agentes."""

    project_name: str | None = None
    description: str | None = None
    requirements: list[str] = field(default_factory=list)
    user_stories: list[str] = field(default_factory=list)
    software_design_document: str | None = None
    architecture: str | None = None
    tasks: list[dict[str, Any]] = field(default_factory=list)
    actions: list["BaseAction"] = field(default_factory=list)
    generated_files: list[dict[str, str]] = field(default_factory=list)
    tests: list[dict[str, Any]] = field(default_factory=list)
    qa_report: str | None = None
    decisions: list[str] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    execution_history: ExecutionHistory = field(default_factory=ExecutionHistory)
    current_agent: str | None = None
    status: str = "CREATED"
