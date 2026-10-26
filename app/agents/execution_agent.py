def run_execution_agent(state):

    evidence = state["retrieved_context"]
    plan = state["remediation_plan"]
    evidence_text = (
        "\n".join(f"- {item}" for item in evidence)
        if evidence
        else "No matching knowledge-base evidence was retrieved."
    )
    plan_text = (
        "\n".join(
            f"{index}. {step}"
            for index, step in enumerate(plan, start=1)
        )
        if plan
        else "No remediation steps were produced."
    )

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
            plan,

        "confidence_score":
            state["confidence_score"],

        "hallucination_detected":
            state["hallucination_detected"],

        "requires_human_review":
            True,

        "remediation_executed":
            False,

        "evidence":
            evidence,

        "ticket_draft": {

            "status": "draft",

            "title": (
                f"[{state['priority']}] {state['title']}"
            ),

            "priority":
                state["priority"],

            "labels": [
                state["domain"],
                state["severity"],
            ],

            "description": (
                f"Incident: {state['incident_id']}\n\n"
                f"Symptoms: {state['masked_description']}\n\n"
                f"Root-cause hypothesis: {state['root_cause']}\n\n"
                f"Evidence:\n{evidence_text}\n\n"
                f"Suggested next steps:\n{plan_text}\n\n"
                f"Confidence score: {state['confidence_score']}\n"
                "Human review required. No remediation was executed."
            ),
        },

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