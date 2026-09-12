import numpy as np


class SimpleVectorStore:
    """
    Small local vector store using NumPy cosine similarity.

    Good for learning and demos.
    In production, replace this with pgvector, Qdrant,
    Pinecone, Weaviate, OpenSearch, etc.
    """

    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.items = []
        self.vectors = []


    def add(self, text: str):
        vector = self.embedding_service.embed(
            text
        )

        self.items.append(text)
        self.vectors.append(vector)


    def search(self, query: str, k: int = 3):
        if not self.items:
            return []

        query_vector = self.embedding_service.embed(
            query
        )

        matrix = np.vstack(
            self.vectors
        ).astype("float32")

        query_norm = np.linalg.norm(
            query_vector
        )

        row_norms = np.linalg.norm(
            matrix,
            axis=1
        )

        denominator = (
            row_norms * query_norm
        )

        denominator = np.where(
            denominator == 0,
            1e-8,
            denominator,
        )

        scores = (
            matrix @ query_vector
        ) / denominator

        k = min(
            k,
            len(self.items)
        )

        top_indices = np.argsort(
            scores
        )[::-1][:k]

        return [
            self.items[int(i)]
            for i in top_indices
        ]
