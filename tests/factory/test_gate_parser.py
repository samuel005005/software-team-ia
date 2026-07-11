from pathlib import Path

from factory.gate_parser import evaluate_gate, evaluate_report
from factory.models import VerdictStatus

QA_APPROVED = """
## Veredicto

**APROBADO**
"""

QA_REJECTED = """
## Bugs encontrados
| ID | Severidad | Descripción | Pasos | Estado |
| BUG-001 | CRITICAL | Falla login | 1. abrir | ABIERTO |

## Veredicto

**RECHAZADO**
"""

REVIEW_OK = """
## Veredicto

**APROBADO**
"""

SECURITY_RISKS = """
## Veredicto

**RIESGOS**
"""


def test_evaluate_qa_approved(tmp_path: Path) -> None:
    path = tmp_path / "QA_REPORT.md"
    path.write_text(QA_APPROVED, encoding="utf-8")
    result = evaluate_report(
        "qa",
        path,
        pass_set=frozenset({"APROBADO"}),
        fail_set=frozenset({"RECHAZADO"}),
        warn_set=frozenset({"CONDICIONAL"}),
        count_critical=True,
    )
    assert result.status == VerdictStatus.PASS


def test_evaluate_qa_critical_bug_fails(tmp_path: Path) -> None:
    path = tmp_path / "QA_REPORT.md"
    path.write_text(QA_REJECTED, encoding="utf-8")
    result = evaluate_report(
        "qa",
        path,
        pass_set=frozenset({"APROBADO"}),
        fail_set=frozenset({"RECHAZADO"}),
        warn_set=frozenset({"CONDICIONAL"}),
        count_critical=True,
    )
    assert result.status == VerdictStatus.FAIL
    assert result.open_critical >= 1


def test_gate_fails_on_pending_tasks() -> None:
    gate = evaluate_gate(pending_tasks=["T-002"], require_qa=False)
    assert gate.passed is False
    assert "T-002" in gate.pending_tasks


def test_gate_passes_all_reports(tmp_path: Path, monkeypatch) -> None:
    from factory import gate_parser

    monkeypatch.setattr(gate_parser, "QA_REPORT", tmp_path / "QA_REPORT.md")
    monkeypatch.setattr(gate_parser, "REVIEW_REPORT", tmp_path / "REVIEW.md")
    monkeypatch.setattr(gate_parser, "SECURITY_REPORT", tmp_path / "SECURITY_REPORT.md")
    (tmp_path / "QA_REPORT.md").write_text(QA_APPROVED, encoding="utf-8")
    (tmp_path / "REVIEW.md").write_text(REVIEW_OK, encoding="utf-8")
    (tmp_path / "SECURITY_REPORT.md").write_text("## Veredicto\n\n**SEGURO**", encoding="utf-8")

    gate = evaluate_gate(require_qa=True, require_review=True, require_security=True, strict=True)
    assert gate.passed is True


def test_gate_warn_security_permissive(tmp_path: Path, monkeypatch) -> None:
    from factory import gate_parser

    monkeypatch.setattr(gate_parser, "SECURITY_REPORT", tmp_path / "SECURITY_REPORT.md")
    (tmp_path / "SECURITY_REPORT.md").write_text(SECURITY_RISKS, encoding="utf-8")

    strict = evaluate_gate(require_qa=False, require_security=True, strict=True)
    assert strict.passed is False

    permissive = evaluate_gate(require_qa=False, require_security=True, strict=False)
    assert permissive.passed is True
