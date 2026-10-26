import unittest

from app.agents.execution_agent import run_execution_agent


class ExecutionAgentTests(unittest.TestCase):
    def test_response_includes_evidence_and_manual_ticket_draft(self):
        state = {
            "incident_id": "INC-1005",
            "title": "Payment API timeout",
            "priority": "P1",
            "severity": "HIGH",
            "domain": "Payments",
            "masked_description": "Payment requests are timing out.",
            "root_cause": "Possible connection pool exhaustion.",
            "remediation_plan": ["Check connection pool usage."],
            "confidence_score": 0.75,
            "hallucination_detected": False,
            "requires_human_review": False,
            "retrieved_context": ["Payment service runbook."],
            "rca_prompt_version": "v1.0.0",
            "planner_prompt_version": "v1.0.0",
            "final_response": None,
        }

        result = run_execution_agent(state)["final_response"]

        self.assertEqual(result["evidence"], ["Payment service runbook."])
        self.assertEqual(result["ticket_draft"]["status"], "draft")
        self.assertTrue(result["requires_human_review"])
        self.assertFalse(result["remediation_executed"])
        self.assertIn("No remediation was executed.", result["ticket_draft"]["description"])


if __name__ == "__main__":
    unittest.main()
