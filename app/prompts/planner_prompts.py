PROMPT_VERSION = "v1.0.0"

PLANNER_PROMPT = """
You are a Senior Incident Response Engineer.

Incident:
{incident}

Root Cause:
{root_cause}

Generate remediation steps.

Rules:
1. Maximum 5 steps.
2. Output JSON array only.
3. No explanations.

Example:

[
"Restart pods",
"Scale deployment"
]
"""