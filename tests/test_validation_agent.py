import unittest
from types import ModuleType
from unittest.mock import Mock, patch


llm_module = ModuleType("app.core.llm")
llm_module.get_llm = Mock()

with patch.dict("sys.modules", {"app.core.llm": llm_module}):
    from app.agents import validation_agent


class ValidationAgentTests(unittest.TestCase):
    def test_missing_evidence_forces_low_confidence_and_human_review(self):
        validation_agent.check_hallucination = Mock()
        state = {
            "retrieved_context": [],
            "root_cause": "Possible connection pool exhaustion.",
            "confidence_score": 0.0,
            "hallucination_detected": False,
            "requires_human_review": False,
        }

        result = validation_agent.run_validation_agent(state)

        self.assertTrue(result["hallucination_detected"])
        self.assertEqual(result["confidence_score"], 0.1)
        self.assertTrue(result["requires_human_review"])
        validation_agent.check_hallucination.assert_not_called()

    def test_recommendations_always_require_human_review(self):
        validation_agent.check_hallucination = Mock(return_value=False)
        state = {
            "retrieved_context": ["Relevant runbook passage."],
            "root_cause": "Possible connection pool exhaustion.",
            "confidence_score": 0.0,
            "hallucination_detected": False,
            "requires_human_review": False,
        }

        result = validation_agent.run_validation_agent(state)

        self.assertEqual(result["confidence_score"], 0.93)
        self.assertTrue(result["requires_human_review"])


if __name__ == "__main__":
    unittest.main()
