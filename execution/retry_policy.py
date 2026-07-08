from quality.quality_decision import QualityDecision


class RetryPolicy:
    """Política de decisión para determinar si un agente debe reintentarse."""

    def __init__(self, max_retries: int = 3) -> None:
        self._max_retries = max_retries

    @property
    def max_retries(self) -> int:
        return self._max_retries

    def should_retry(
        self,
        quality_decision: QualityDecision,
        retry_count: int,
    ) -> bool:
        if not quality_decision.retry:
            return False

        if retry_count >= self._max_retries:
            return False

        return True
