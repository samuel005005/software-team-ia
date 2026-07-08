import unittest

from agents.analyst_agent import AnalystAgent
from agents.architect_agent import ArchitectAgent
from agents.developer_agent import DeveloperAgent
from agents.qa_agent import QAAgent
from context.context_builder import ContextBuilder
from state.project_state import ProjectState


class ContextBuilderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
            requirements=["Gestión de citas", "Perfiles de clientes"],
            user_stories=["Como usuario quiero registrarme"],
            software_design_document="SDD de prueba",
            architecture="Flutter + FastAPI",
            tasks=[{"id": 1, "title": "Configurar Flutter"}],
        )

    def test_for_analyst_contains_expected_inputs(self) -> None:
        context = ContextBuilder.for_analyst(self.state)

        self.assertEqual(context.agent_name, "Business Analyst")
        self.assertEqual(context.inputs["project_name"], "barberia-app")
        self.assertEqual(context.inputs["description"], self.state.description)
        self.assertEqual(context.inputs["requirements"], self.state.requirements)
        self.assertTrue(context.constraints)

    def test_for_architect_contains_user_stories(self) -> None:
        context = ContextBuilder.for_architect(self.state)

        self.assertEqual(context.agent_name, "Software Architect")
        self.assertEqual(context.inputs["user_stories"], self.state.user_stories)

    def test_for_developer_contains_sdd(self) -> None:
        context = ContextBuilder.for_developer(self.state)

        self.assertEqual(context.agent_name, "Flutter Developer")
        self.assertEqual(context.inputs["software_design_document"], "SDD de prueba")
        self.assertEqual(context.inputs["architecture"], "Flutter + FastAPI")

    def test_for_qa_contains_validation_inputs(self) -> None:
        context = ContextBuilder.for_qa(self.state)

        self.assertEqual(context.agent_name, "QA Engineer")
        self.assertEqual(context.inputs["user_stories_count"], 1)
        self.assertTrue(context.inputs["has_architecture"])
        self.assertEqual(context.inputs["tasks_count"], 1)

    def test_build_dispatches_by_agent_type(self) -> None:
        context = ContextBuilder.build(AnalystAgent(), self.state)
        self.assertEqual(context.agent_name, "Business Analyst")

        context = ContextBuilder.build(ArchitectAgent(), self.state)
        self.assertEqual(context.agent_name, "Software Architect")

        context = ContextBuilder.build(DeveloperAgent(), self.state)
        self.assertEqual(context.agent_name, "Flutter Developer")

        context = ContextBuilder.build(QAAgent(), self.state)
        self.assertEqual(context.agent_name, "QA Engineer")


if __name__ == "__main__":
    unittest.main()
