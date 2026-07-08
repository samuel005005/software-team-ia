import unittest

from planning.execution_plan import ExecutionPlan


class ExecutionPlanTestCase(unittest.TestCase):
    def test_creation_with_defaults(self) -> None:
        plan = ExecutionPlan()

        self.assertEqual(plan.nodes, [])
        self.assertEqual(plan.metadata, {})

    def test_add_node(self) -> None:
        plan = ExecutionPlan()
        plan.add_node("analyst")
        plan.add_node("architect")

        self.assertEqual(plan.nodes, ["analyst", "architect"])

    def test_to_dict(self) -> None:
        plan = ExecutionPlan(metadata={"objective": "barberia-app"})
        plan.add_node("analyst")
        plan.add_node("qa")

        data = plan.to_dict()

        self.assertEqual(data["nodes"], ["analyst", "qa"])
        self.assertEqual(data["metadata"]["objective"], "barberia-app")

    def test_to_dict_returns_copies(self) -> None:
        plan = ExecutionPlan()
        plan.add_node("developer")

        data = plan.to_dict()
        data["nodes"].append("extra")
        data["metadata"]["new"] = True

        self.assertEqual(plan.nodes, ["developer"])
        self.assertEqual(plan.metadata, {})


if __name__ == "__main__":
    unittest.main()
