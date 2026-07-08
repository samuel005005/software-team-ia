from agents.developer_agent import DeveloperAgent
from llm.llm_config import LLMConfig
from llm.provider_factory import ProviderFactory
from orchestrator.orchestrator import Orchestrator
from planning.planner_agent import PlannerAgent
from agents.agent_registry import create_default_registry
from state.project_state import ProjectState
from workflows.software_creation import (
    build_agents_for_software_creation,
    build_graph_from_plan,
    create_memory_store,
    create_project_workspace,
    create_tool_executor,
)


def main() -> None:
    config = LLMConfig.from_env()
    config.validate()

    provider = ProviderFactory.from_config(config)
    print("=" * 50)
    print("CONFIGURACIÓN LLM")
    print("=" * 50)
    print(f"  Provider: {config.provider_name}")
    print(f"  Model: {config.model or 'default del provider'}")
    print(f"  Runtime provider: {provider.provider_name}")

    state = ProjectState(
        project_name="barberia-app",
        description="Crear una aplicación móvil para administrar una barbería",
        status="CREATED",
    )

    memory_store = create_memory_store()
    workspace = create_project_workspace()
    registry = create_default_registry()
    plan = PlannerAgent(llm_provider=provider, registry=registry).plan(state.description)
    agents = build_agents_for_software_creation(provider, memory_store, workspace)
    graph = build_graph_from_plan(plan, agents)
    tool_executor = create_tool_executor()
    orchestrator = Orchestrator(graph.get_agents(), tool_executor=tool_executor)
    final_state = orchestrator.run(state)

    developer = agents.get("developer")
    artifact_source = (
        developer.last_artifact_source
        if isinstance(developer, DeveloperAgent)
        else "unknown"
    )

    print("\n" + "=" * 50)
    print("PLANNER")
    print("=" * 50)
    print(f"  Source: {plan.metadata.get('source', 'unknown')}")
    print(f"  Provider: {plan.metadata.get('provider', provider.provider_name)}")
    print(f"  Nodes: {' → '.join(plan.nodes)}")

    print("\n" + "=" * 50)
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
        description = task.get("description")
        if description:
            print(f"      {description}")

    print("\n" + "=" * 50)
    print("ARTEFACTOS GENERADOS")
    print("=" * 50)
    print(f"  Source: {artifact_source}")
    for file_info in final_state.generated_files:
        print(f"  - {file_info['path']}")

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
