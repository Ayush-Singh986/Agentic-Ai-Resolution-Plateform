def run_triage_agent(state):

    description = state[
        "masked_description"
    ].lower()

    if "payment" in description:

        severity = "HIGH"
        priority = "P1"
        domain = "Payments"

    elif "redis" in description:

        severity = "HIGH"
        priority = "P1"
        domain = "Caching"

    else:

        severity = "MEDIUM"
        priority = "P2"
        domain = "General"

    state["severity"] = severity
    state["priority"] = priority
    state["domain"] = domain

    return state