from typing import TYPE_CHECKING

from agents.agent_result import AgentResult
from execution.execution_node import ExecutionNode
from execution.execution_policy import DefaultExecutionPolicy, ExecutionPolicy
from execution.retry_context import RetryContext
from execution.retry_policy import RetryPolicy
from quality.quality_decision import QualityDecision

if TYPE_CHECKING:
    from execution.execution_graph import ExecutionGraph


class RetryAwareExecutionPolicy(ExecutionPolicy):
    """Política que puede reintentar el nodo actual según calidad y RetryPolicy."""

    def __init__(self, retry_policy: RetryPolicy | None = None) -> None:
        self._retry_policy = retry_policy or RetryPolicy()
        self._default_policy = DefaultExecutionPolicy()

    @property
    def retry_policy(self) -> RetryPolicy:
        return self._retry_policy

    def choose_next(
        self,
        current_node: ExecutionNode,
        agent_result: AgentResult | None = None,
        execution_graph: "ExecutionGraph | None" = None,
        quality_decision: QualityDecision | None = None,
        retry_context: RetryContext | None = None,
    ) -> ExecutionNode | None:
        if quality_decision is not None and quality_decision.retry:
            retry_count = retry_context.retry_count if retry_context is not None else 0
            if self._retry_policy.should_retry(quality_decision, retry_count):
                return current_node

        return self._default_policy.choose_next(
            current_node,
            agent_result,
            execution_graph,
            quality_decision=quality_decision,
            retry_context=retry_context,
        )
