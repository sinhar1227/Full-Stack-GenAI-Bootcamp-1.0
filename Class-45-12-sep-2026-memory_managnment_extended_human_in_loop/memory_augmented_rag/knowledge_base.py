from embeddings import embedding_service
from vector_store import SimpleVectorStore


class KnowledgeBase:
    """
    RAG knowledge base for business/domain documents.
    """

    def __init__(self):
        self.store = SimpleVectorStore(
            embedding_service
        )


    def add_document(
        self,
        text: str,
    ):
        self.store.add(
            text.strip()
        )


    def search(
        self,
        query: str,
        k: int = 3,
    ):
        return self.store.search(
            query,
            k
        )


knowledge_base = KnowledgeBase()
