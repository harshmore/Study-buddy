from langchain_huggingface import HuggingFaceEmbeddings
from src.config.settings import settings


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
