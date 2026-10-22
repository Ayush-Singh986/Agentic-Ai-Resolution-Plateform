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

        plan = json.loads(
            response.content
        )

    except Exception:

        plan = [

            "Restart service",

            "Scale deployment",

            "Monitor metrics"
        ]

    state["remediation_plan"] = plan

    state["planner_prompt_version"] = (
        PROMPT_VERSION
    )

    return state