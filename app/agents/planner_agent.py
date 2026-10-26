import json

from app.core.llm import get_llm

from app.prompts.planner_prompts import (
    PLANNER_PROMPT,
    PROMPT_VERSION
)

from app.observability.logger import (
    logger
)

llm = get_llm()


def run_planner_agent(state):

    prompt = PLANNER_PROMPT.format(

        incident=state[
            "masked_description"
        ],

        root_cause=state[
            "root_cause"
        ]
    )

    logger.info(
        f"Planner Prompt Version:"
        f"{PROMPT_VERSION}"
    )

    response = llm.invoke(
        prompt
    )

    try:
        plan = json.loads(response.content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "The planner returned invalid JSON; no remediation plan was produced."
        ) from exc

    if (
        not isinstance(plan, list)
        or len(plan) > 5
        or not all(
            isinstance(step, str) and step.strip()
            for step in plan
        )
    ):
        raise ValueError(
            "The planner response must be a JSON array of up to five non-empty steps."
        )

    state["remediation_plan"] = plan

    state["planner_prompt_version"] = (
        PROMPT_VERSION
    )

    return state