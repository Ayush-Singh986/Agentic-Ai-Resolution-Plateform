TOKEN_COST_PER_1K = 0.0005


def estimate_cost(
        prompt_tokens,
        completion_tokens
):

    total = (
        prompt_tokens +
        completion_tokens
    )

    cost = (
        total / 1000
    ) * TOKEN_COST_PER_1K

    return round(cost, 6)