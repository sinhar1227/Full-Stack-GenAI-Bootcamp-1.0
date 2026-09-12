from embeddings import embedding_service
from vector_store import SimpleVectorStore


class SemanticMemory:
    """
    User-level semantic memory.

    Each user gets a separate vector store containing
    previous interactions.
    """

    def __init__(self):
        self.users = {}


    def _get_store(
        self,
        user_id: str,
    ):
        if user_id not in self.users:
            self.users[
                user_id
            ] = SimpleVectorStore(
                embedding_service
            )

        return self.users[
            user_id
        ]


    def add_memory(
        self,
        user_id: str,
        text: str,
    ):
        self._get_store(
            user_id
        ).add(
            text
        )


    def search(
        self,
        user_id: str,
        query: str,
        k: int = 3,
    ):
        return self._get_store(
            user_id
        ).search(
            query,
            k
        )


semantic_memory = SemanticMemory()
