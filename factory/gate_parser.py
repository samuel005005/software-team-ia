"""Lee veredictos de reportes SDD para factory gate."""

import re
from pathlib import Path

from factory.config import DOCS_DIR
from factory.models import GateResult, RoleVerdict, VerdictStatus

QA_REPORT = DOCS_DIR / "QA_REPORT.md"
REVIEW_REPORT = DOCS_DIR / "REVIEW.md"
SECURITY_REPORT = DOCS_DIR / "SECURITY_REPORT.md"

_VERDICT_SECTION = re.compile(r"^##\s+Veredicto\s*$", re.MULTILINE | re.IGNORECASE)
_BOLD_VERDICT = re.compile(r"\*\*([^*]+)\*\*")

_QA_PASS = frozenset({"APROBADO", "APPROVED", "PASS"})
_QA_FAIL = frozenset({"RECHAZADO", "REJECTED", "FAIL", "FAILED"})
_QA_WARN = frozenset({"CONDICIONAL", "CONDITIONAL"})

_REVIEW_PASS = frozenset({"APROBADO", "APPROVED"})
_REVIEW_FAIL = frozenset({"CAMBIOS REQUERIDOS", "CHANGES REQUIRED", "RECHAZADO", "REJECTED"})

_SECURITY_PASS = frozenset({"SEGURO", "SECURE", "SAFE"})
_SECURITY_FAIL = frozenset({"INSEGURO", "INSECURE", "UNSAFE"})
_SECURITY_WARN = frozenset({"RIESGOS", "RISKS", "AT RISK"})

_CRITICAL_BUG = re.compile(
    r"^\|\s*BUG-\d+\s*\|\s*CRITICAL\b",
    re.MULTILINE | re.IGNORECASE,
)
_OPEN_BUG = re.compile(r"\bABIERTO\b|\bOPEN\b", re.IGNORECASE)
_SEC_CRITICAL = re.compile(
    r"^\|\s*SEC-\d+\s*\|\s*CRITICAL\b",
    re.MULTILINE | re.IGNORECASE,
)


def _read_report(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _extract_verdict_line(text: str) -> str | None:
    section = _VERDICT_SECTION.search(text)
    if not section:
        for line in text.splitlines():
            if "veredicto" in line.lower() and "**" in line:
                return line.strip()
        return None

    rest = text[section.end() :]
    next_section = re.search(r"\n##\s+", rest)
    block = rest[: next_section.start()] if next_section else rest
    for line in block.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return None


def _normalize_verdict(line: str | None) -> str | None:
    if not line:
        return None
    match = _BOLD_VERDICT.search(line)
    if match:
        return match.group(1).strip().upper()
    return line.strip().upper()


def _count_critical_open_bugs(text: str) -> int:
    count = 0
    for line in text.splitlines():
        if _CRITICAL_BUG.match(line) and _OPEN_BUG.search(line):
            count += 1
    return count


def _count_critical_security(text: str) -> int:
    return len(_SEC_CRITICAL.findall(text))


def _classify(verdict: str | None, *, pass_set: frozenset[str], fail_set: frozenset[str], warn_set: frozenset[str] | None = None) -> VerdictStatus:
    if not verdict:
        return VerdictStatus.MISSING
    if verdict in pass_set:
        return VerdictStatus.PASS
    if verdict in fail_set:
        return VerdictStatus.FAIL
    if warn_set and verdict in warn_set:
        return VerdictStatus.WARN
    # Substring fallback (ej. "PASS (smoke T-001)")
    for token in pass_set:
        if token in verdict:
            return VerdictStatus.PASS
    for token in fail_set:
        if token in verdict:
            return VerdictStatus.FAIL
    if warn_set:
        for token in warn_set:
            if token in verdict:
                return VerdictStatus.WARN
    return VerdictStatus.WARN


def evaluate_report(
    role: str,
    path: Path,
    *,
    pass_set: frozenset[str],
    fail_set: frozenset[str],
    warn_set: frozenset[str] | None = None,
    count_critical: bool = False,
) -> RoleVerdict:
    text = _read_report(path)
    if text is None:
        return RoleVerdict(
            role=role,
            status=VerdictStatus.MISSING,
            verdict=None,
            message=f"Falta {path.relative_to(DOCS_DIR.parent)}",
        )

    verdict_line = _extract_verdict_line(text)
    verdict = _normalize_verdict(verdict_line)
    status = _classify(verdict, pass_set=pass_set, fail_set=fail_set, warn_set=warn_set)
    critical = _count_critical_open_bugs(text) if count_critical and role == "qa" else 0
    if role == "security":
        critical = _count_critical_security(text)

    message = verdict or "sin veredicto explícito"
    if critical > 0:
        status = VerdictStatus.FAIL
        message = f"{message} · {critical} hallazgo(s) CRITICAL abierto(s)"

    return RoleVerdict(
        role=role,
        status=status,
        verdict=verdict,
        message=message,
        open_critical=critical,
    )


def evaluate_gate(
    *,
    require_qa: bool = True,
    require_review: bool = False,
    require_security: bool = False,
    pending_tasks: list[str] | None = None,
    scope_label: str = "proyecto completo",
    strict: bool = True,
) -> GateResult:
    """Evalúa si el proyecto puede entregarse según reportes y tareas."""
    verdicts: list[RoleVerdict] = []
    messages: list[str] = []
    pending = tuple(pending_tasks or ())

    if pending:
        messages.append(f"Tareas incompletas en alcance: {', '.join(pending)}")

    checks: list[tuple[str, Path, bool, frozenset[str], frozenset[str], frozenset[str] | None, bool]] = []
    if require_qa:
        checks.append(("qa", QA_REPORT, True, _QA_PASS, _QA_FAIL, _QA_WARN, True))
    if require_review:
        checks.append(("reviewer", REVIEW_REPORT, True, _REVIEW_PASS, _REVIEW_FAIL, None, False))
    if require_security:
        checks.append(("security", SECURITY_REPORT, True, _SECURITY_PASS, _SECURITY_FAIL, _SECURITY_WARN, True))

    for role, path, _required, pset, fset, wset, count_crit in checks:
        rv = evaluate_report(role, path, pass_set=pset, fail_set=fset, warn_set=wset, count_critical=count_crit)
        verdicts.append(rv)
        if rv.status == VerdictStatus.MISSING:
            messages.append(f"{role}: reporte ausente")
        elif rv.status == VerdictStatus.FAIL:
            messages.append(f"{role}: {rv.message}")
        elif rv.status == VerdictStatus.WARN:
            messages.append(f"{role}: {rv.message} (advertencia)")

    passed = True
    if pending:
        passed = False
    for rv in verdicts:
        if rv.status == VerdictStatus.FAIL:
            passed = False
        elif rv.status == VerdictStatus.MISSING and strict:
            passed = False
        elif rv.status == VerdictStatus.WARN and strict:
            passed = False

    return GateResult(
        passed=passed,
        verdicts=tuple(verdicts),
        pending_tasks=pending,
        scope_label=scope_label,
        messages=tuple(messages),
    )
