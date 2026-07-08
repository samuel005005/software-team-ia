from agents.base_agent import BaseAgent
from state.project_state import ProjectState


class QAAgent(BaseAgent):
    """Agente que valida la completitud del trabajo previo y genera un reporte QA."""

    @property
    def name(self) -> str:
        return "QA Engineer"

    def process(self, state: ProjectState) -> ProjectState:
        state.logs.append(f"[{self.name}] Iniciando revisión de calidad")

        has_user_stories = bool(state.user_stories)
        has_architecture = bool(state.architecture)
        has_tasks = bool(state.tasks)

        checks = [
            ("Historias de usuario", has_user_stories, len(state.user_stories)),
            ("Arquitectura técnica", has_architecture, 1 if has_architecture else 0),
            ("Tareas de desarrollo", has_tasks, len(state.tasks)),
        ]

        passed_checks = sum(1 for _, passed, _ in checks if passed)
        total_checks = len(checks)
        all_passed = passed_checks == total_checks

        report_lines = [
            "=== REPORTE QA ===",
            f"Estado general: {'APROBADO' if all_passed else 'RECHAZADO'}",
            f"Verificaciones: {passed_checks}/{total_checks}",
            "",
            "Detalle de verificaciones:",
        ]

        for label, passed, count in checks:
            status = "OK" if passed else "FALTA"
            report_lines.append(f"  - {label}: {status} ({count} elemento(s))")

        if all_passed:
            report_lines.extend(
                [
                    "",
                    "Conclusión: El proyecto cuenta con la documentación mínima",
                    "requerida para iniciar el desarrollo.",
                ]
            )
        else:
            report_lines.extend(
                [
                    "",
                    "Conclusión: Faltan artefactos necesarios antes de continuar.",
                ]
            )

        state.qa_report = "\n".join(report_lines)
        state.logs.append(f"[{self.name}] Reporte QA generado: {passed_checks}/{total_checks} OK")

        return state

    def build_output_summary(self, state: ProjectState) -> str:
        return "Reporte QA generado" if state.qa_report else "Sin reporte QA"
