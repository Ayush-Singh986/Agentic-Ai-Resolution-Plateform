from app.governance.hallucination_checker import (
    check_hallucination
)

from app.governance.confidence_scoring import (
    calculate_confidence
)


def run_validation_agent(state):

    context = "\n".join(
        state["retrieved_context"]
    )

    hallucinated = (
        not context
        or check_hallucination(
            state["root_cause"],
            context,
        )
    )

    retrieval_score = 0.90 if context else 0.0

    validation_score = 0.95 \
        if not hallucinated else 0.60

    confidence = calculate_confidence(
        retrieval_score=retrieval_score,
        hallucination_penalty=0.20
        if hallucinated else 0.0,
        validation_score=validation_score
    )

    state["hallucination_detected"] = hallucinated

    state["confidence_score"] = confidence

    state["requires_human_review"] = True

    return state