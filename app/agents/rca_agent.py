from app.core.llm import get_llm

from app.prompts.rca_prompts import (
    RCA_PROMPT,
    PROMPT_VERSION
)

from app.observability.logger import (
    logger
)

llm = get_llm()


def run_rca_agent(state):

    context = "\n".join(
        state["retrieved_context"]
    )

    prompt = RCA_PROMPT.format(
        incident=state[
            "masked_description"
        ],

        context=context
    )

    logger.info(
        f"Executing RCA Prompt Version: "
        f"{PROMPT_VERSION}"
    )

    response = llm.invoke(
        prompt
    )

    state["root_cause"] = (
        response.content
    )

    state["rca_prompt_version"] = (
        PROMPT_VERSION
    )

    return state