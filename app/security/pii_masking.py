import re


EMAIL_PATTERN = r'[\w\.-]+@[\w\.-]+\.\w+'
PHONE_PATTERN = r'\+?\d[\d\s-]{8,15}'
IP_PATTERN = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'


def mask_pii(text: str) -> str:

    if not text:
        return text

    text = re.sub(
        EMAIL_PATTERN,
        '[EMAIL_MASKED]',
        text
    )

    text = re.sub(
        PHONE_PATTERN,
        '[PHONE_MASKED]',
        text
    )

    text = re.sub(
        IP_PATTERN,
        '[IP_MASKED]',
        text
    )

    return text