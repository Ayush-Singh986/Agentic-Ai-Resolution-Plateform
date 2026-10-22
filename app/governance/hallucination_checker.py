from app.core.llm import get_llm

llm = get_llm()

# LLM-as-a-judge Evaluation

def check_hallucination(
        generated_answer: str,
        context: str
):

    prompt = f"""
You are an AI evaluator.

Retrieved Context:
{context}

Generated Answer:
{generated_answer}

Determine whether the generated answer is fully supported by the retrieved context.

Rules:
- Return ONLY TRUE if answer contains unsupported facts.
- Return ONLY FALSE if answer is grounded in context.

Output only:
TRUE or FALSE
"""

    response = llm.invoke(prompt)

    verdict = response.content.strip().upper()

    return verdict == "TRUE"