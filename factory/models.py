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


@dataclass(frozen=True)
class RunResult:
    role: FactoryRole
    task_id: str | None
    status: str
    agent_id: str | None
    summary: str | None
    error: str | None = None
