from orchestrator.orchestrator import Orchestrator
from state.project_state import ProjectState
from workflows.software_creation import create_tool_executor, get_software_creation_agents


def main() -> None:
    state = ProjectState(
        project_name="barberia-app",
        description="Crear una aplicación móvil para administrar una barbería",
        status="CREATED",
    )

    agents = get_software_creation_agents()
    tool_executor = create_tool_executor()
    orchestrator = Orchestrator(agents, tool_executor=tool_executor)
    final_state = orchestrator.run(state)

    print("=" * 50)
    print("HISTORIAS GENERADAS")
    print("=" * 50)
    for story in final_state.user_stories:
        print(f"  - {story}")

    print("\n" + "=" * 50)
    print("SOFTWARE DESIGN DOCUMENT")
    print("=" * 50)
    print(final_state.software_design_document or "No generado")

    print("\n" + "=" * 50)
    print("ARQUITECTURA")
    print("=" * 50)
    print(final_state.architecture or "No definida")

    print("\n" + "=" * 50)
    print("TAREAS")
    print("=" * 50)
    for task in final_state.tasks:
        print(f"  [{task['id']}] {task['title']} ({task['status']})")
        print(f"      {task['description']}")

    print("\n" + "=" * 50)
    print("REPORTE QA")
    print("=" * 50)
    print(final_state.qa_report or "No generado")

    print("\n" + "=" * 50)
    print("EXECUTION HISTORY")
    print("=" * 50)
    for record in final_state.execution_history.get_all():
        duration = f" ({record.duration_ms}ms)" if record.duration_ms is not None else ""
        print(f"{record.agent_name} {record.status}{duration}")
        if record.output_summary:
            print(f"  Output: {record.output_summary}")
        if record.errors:
            for error in record.errors:
                print(f"  Error: {error}")

    print("\n" + "=" * 50)
    print("LOGS")
    print("=" * 50)
    for log in final_state.logs:
        print(f"  {log}")


if __name__ == "__main__":
    main()
