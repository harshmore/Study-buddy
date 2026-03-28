from src.rag.loader import load_document
from src.rag.splitter import split_documents
from src.rag.embeddings import get_embeddings
from src.rag.vector_store import create_vector_store
from src.rag.retriever import get_retriever


class RAGPipeline:
    def __init__(self, top_k=8, max_tokens=2000):
        self.retriever = None
        self.top_k = top_k
        self.max_tokens = max_tokens

    def ingest(self, uploaded_file):
        documents = load_document(uploaded_file)

        for i, doc in enumerate(documents):
            doc.metadata["source"] = uploaded_file.name
            doc.metadata["doc_id"] = i

        chunks = split_documents(documents)

        embeddings = get_embeddings()
        vector_store = create_vector_store(chunks, embeddings)

        self.retriever = get_retriever(vector_store, k=self.top_k)

    def build_quiz_context(self):
        if not self.retriever:
            raise ValueError("Call ingest() first.")

        query = self._build_query()

        docs = self.retriever.invoke(query)

        texts = [doc.page_content for doc in docs]

        texts = list(dict.fromkeys(texts))

        texts = self._filter_chunks(texts)

        texts = self._diversify_chunks(texts)

        texts = self._limit_tokens(texts)

        return "\n\n".join(texts)

    def _build_query(self):
        return f"""
        Extract the most important, diverse, and testable concepts for a quiz.

        Focus on:
        - core concepts
        - cause-effect relationships
        - comparisons
        - real-world applications
        """

    def _filter_chunks(self, texts):
        return [t for t in texts if len(t.split()) > 30]

    def _diversify_chunks(self, texts):
        seen = set()
        diversified = []

        for t in texts:
            key = t[:100]
            if key not in seen:
                diversified.append(t)
                seen.add(key)

        return diversified

    def _limit_tokens(self, texts):
        total_chars = 0
        limited = []

        for text in texts:
            total_chars += len(text)
            if total_chars > self.max_tokens:
                break
            limited.append(text)

        return limited
