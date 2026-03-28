def get_retriever(vector_store, k=5):
    return vector_store.as_retriever(search_kwargs={"k": k})
