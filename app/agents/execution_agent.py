def run_execution_agent(state):

    state["final_response"] = {

        "incident_id":
            state["incident_id"],

        "severity":
            state["severity"],

        "domain":
            state["domain"],

        "priority":
            state["priority"],

        "root_cause":
            state["root_cause"],

        "remediation_plan":
            state["remediation_plan"],

        "confidence_score":
            state["confidence_score"],

        "hallucination_detected":
            state["hallucination_detected"],

        "requires_human_review":
            state["requires_human_review"],

        "prompt_versions": {

            "rca":
                state[
                    "rca_prompt_version"
                ],

            "planner":
                state[
                    "planner_prompt_version"
                ]
        }
    }

    return state