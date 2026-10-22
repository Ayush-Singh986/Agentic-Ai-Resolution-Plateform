SUSPICIOUS_PATTERNS = [

    "ignore previous instructions",
    "forget all instructions",
    "system prompt",
    "reveal prompt",
    "jailbreak",
    "bypass security",
    "act as root",
    "disable safety"
]


def detect_prompt_injection(text: str):

    text = text.lower()

    for pattern in SUSPICIOUS_PATTERNS:

        if pattern in text:
            return True

    return False