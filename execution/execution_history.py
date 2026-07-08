from execution.execution_record import ExecutionRecord


class ExecutionHistory:
    """Almacena y gestiona el historial de ejecución de agentes."""

    def __init__(self) -> None:
        self._records: list[ExecutionRecord] = []

    def add(self, record: ExecutionRecord) -> None:
        self._records.append(record)

    def get_all(self) -> list[ExecutionRecord]:
        return list(self._records)

    def get_last(self) -> ExecutionRecord | None:
        if not self._records:
            return None
        return self._records[-1]

    def discard_from(self, index: int) -> None:
        """Elimina registros desde el índice indicado."""
        if index < 0:
            return
        self._records = self._records[:index]
