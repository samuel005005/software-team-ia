import unittest
from datetime import datetime, timedelta

from execution.execution_history import ExecutionHistory
from execution.execution_record import ExecutionRecord, ExecutionStatus


class ExecutionHistoryTestCase(unittest.TestCase):
    def test_starts_empty(self) -> None:
        history = ExecutionHistory()
        self.assertEqual(history.get_all(), [])
        self.assertIsNone(history.get_last())

    def test_add_and_get_all(self) -> None:
        history = ExecutionHistory()
        record = ExecutionRecord(
            agent_name="AnalystAgent",
            started_at=datetime(2026, 7, 7, 10, 0, 0),
            finished_at=datetime(2026, 7, 7, 10, 0, 1),
            input_summary="project=test",
            output_summary="3 historias generadas",
            status=ExecutionStatus.SUCCESS,
        )

        history.add(record)
        records = history.get_all()

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].agent_name, "AnalystAgent")
        self.assertEqual(records[0].status, ExecutionStatus.SUCCESS)

    def test_get_last(self) -> None:
        history = ExecutionHistory()
        history.add(ExecutionRecord(agent_name="AnalystAgent", started_at=datetime.now()))
        history.add(ExecutionRecord(agent_name="QAAgent", started_at=datetime.now()))

        last = history.get_last()
        self.assertIsNotNone(last)
        assert last is not None
        self.assertEqual(last.agent_name, "QAAgent")

    def test_record_duration_ms_calculated_on_finish(self) -> None:
        started = datetime(2026, 7, 7, 10, 0, 0)
        finished = started + timedelta(milliseconds=250)
        record = ExecutionRecord(
            agent_name="DeveloperAgent",
            started_at=started,
            finished_at=finished,
            status=ExecutionStatus.SUCCESS,
        )

        self.assertEqual(record.duration_ms, 250)

    def test_execution_status_constants(self) -> None:
        self.assertEqual(ExecutionStatus.RUNNING, "RUNNING")
        self.assertEqual(ExecutionStatus.SUCCESS, "SUCCESS")
        self.assertEqual(ExecutionStatus.FAILED, "FAILED")
        self.assertEqual(ExecutionStatus.RETRY, "RETRY")
        self.assertEqual(ExecutionStatus.TIMEOUT, "TIMEOUT")
        self.assertEqual(ExecutionStatus.CANCELLED, "CANCELLED")
        self.assertEqual(ExecutionStatus.SKIPPED, "SKIPPED")

    def test_errors_is_list(self) -> None:
        record = ExecutionRecord(
            agent_name="AnalystAgent",
            started_at=datetime.now(),
            status=ExecutionStatus.FAILED,
            errors=["Error de prueba"],
        )

        self.assertIsInstance(record.errors, list)
        self.assertEqual(record.errors, ["Error de prueba"])


if __name__ == "__main__":
    unittest.main()
