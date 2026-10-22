from langchain_groq import ChatGroq

from app.core.config import settings


def get_llm():

    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.MODEL_NAME,
        temperature=0
    )

    return llm