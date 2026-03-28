import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    MODELS = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "gpt-4o-mini",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "meta-llama/llama-guard-4-12b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    TEMPERATURE = 0.9

    MAX_RETRIES = 3


settings = Settings()
