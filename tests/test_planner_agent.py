import unittest
from types import ModuleType
from unittest.mock import Mock, patch


llm_module = ModuleType("app.core.llm")
llm_module.get_llm = Mock()

with patch.dict("sys.modules", {"app.core.llm": llm_module}):
    from app.agents import planner_agent


class PlannerAgentTests(unittest.TestCase):
    def setUp(self):
        planner_agent.llm = Mock()

    def test_parses_a_valid_plan(self):
        planner_agent.llm.invoke.return_value.content = (
            '["Check the connection pool.", "Review deployment changes."]'
        )
        state = {
            "masked_description": "Payment requests are timing out.",
            "root_cause": "Possible connection pool exhaustion.",
        }

        result = planner_agent.run_planner_agent(state)

        self.assertEqual(
            result["remediation_plan"],
            ["Check the connection pool.", "Review deployment changes."],
        )

    def test_invalid_json_fails_instead_of_returning_generic_actions(self):
        planner_agent.llm.invoke.return_value.content = "not JSON"
        state = {
            "masked_description": "Payment requests are timing out.",
            "root_cause": "Possible connection pool exhaustion.",
        }

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            planner_agent.run_planner_agent(state)

    def test_rejects_non_string_or_too_many_steps(self):
        planner_agent.llm.invoke.return_value.content = '["Check", 7]'
        state = {
            "masked_description": "Payment requests are timing out.",
            "root_cause": "Possible connection pool exhaustion.",
        }

        with self.assertRaisesRegex(ValueError, "up to five"):
            planner_agent.run_planner_agent(state)


if __name__ == "__main__":
    unittest.main()
