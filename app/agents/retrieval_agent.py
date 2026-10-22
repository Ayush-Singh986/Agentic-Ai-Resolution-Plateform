from app.retrieval.retriever import (
    retrieve_context
)


def run_retrieval_agent(state):

    context = retrieve_context(
        state["masked_description"]
    )

    state["retrieved_context"] = context

    return state