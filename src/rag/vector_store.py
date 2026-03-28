from langchain_community.vectorstores import FAISS


def create_vector_store(documents, embeddings):
    return FAISS.from_documents(documents, embeddings)
