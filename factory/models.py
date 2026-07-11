from dataclasses import dataclass
from enum import Enum
from typing import Literal

ModelTier = Literal["smart", "fast", "cheap"]


class FactoryRole(str, Enum):
    PRODUCT_MANAGER = "product_manager"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    QA = "qa"
    REVIEWER = "reviewer"
    SECURITY = "security"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class TaskItem:
    task_id: str
    title: str
    story: str | None
    owner: str
    status: TaskStatus
    line_number: int
    skip_analyze: bool = False
    force_analyze: bool = False
    phase: str | None = None


class VerdictStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    MISSING = "missing"


@dataclass(frozen=True)
class RoleVerdict:
    role: str
    status: VerdictStatus
    verdict: str | None
    message: str
    open_critical: int = 0


@dataclass(frozen=True)
class GateResult:
    passed: bool
    verdicts: tuple[RoleVerdict, ...]
    pending_tasks: tuple[str, ...]
    scope_label: str
    messages: tuple[str, ...]


@dataclass(frozen=True)
class QAScope:
    """Alcance opcional para validación QA / release."""

    phase: str | None = None
    story_ids: tuple[str, ...] = ()
    task_ids: tuple[str, ...] = ()

    def label(self) -> str:
        parts: list[str] = []
        if self.phase:
            parts.append(f"fase={self.phase}")
        if self.story_ids:
            parts.append("US=" + ",".join(self.story_ids))
        if self.task_ids:
            parts.append("tareas=" + ",".join(self.task_ids))
        return " · ".join(parts) if parts else "proyecto completo"


@dataclass(frozen=True)
class RunResult:
    role: FactoryRole
    task_id: str | None
    status: str
    agent_id: str | None
    summary: str | None
    error: str | None = None
