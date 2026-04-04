from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from src.config.settings import settings


def get_groq_llm(model, api_key):
    return ChatGroq(
        api_key=api_key if api_key else settings.GROQ_API_KEY,
        model=model,
        temperature=settings.TEMPERATURE,
    )


def get_openai_llm(model):
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY, model=model, temperature=settings.TEMPERATURE
    )
