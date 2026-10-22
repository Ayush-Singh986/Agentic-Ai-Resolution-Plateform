PROMPT_VERSION = "v1.0.0"

RCA_PROMPT = """
You are a Senior Site Reliability Engineer.

Incident Description:
{incident}

Historical Context:
{context}

Perform Root Cause Analysis.

Rules:
1. Use ONLY provided context.
2. If insufficient information exists, say:
   "Insufficient evidence."
3. Maximum 50 words.

Return concise answer only.
"""