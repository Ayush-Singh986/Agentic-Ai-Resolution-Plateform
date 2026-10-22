def calculate_confidence(
        retrieval_score: float = 0.9,
        hallucination_penalty: float = 0,
        validation_score: float = 0.9
):

    score = (
        retrieval_score * 0.5 +
        validation_score * 0.5
    )

    score -= hallucination_penalty

    score = max(0.0, min(1.0, score))

    return round(score, 2)