import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    MODELS = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    TEMPERATURE = 0.9

    MAX_RETRIES = 3


settings = Settings()
