import hashlib
import numpy as np

from config import (
    EMBEDDING_MODEL,
    USE_FAKE_MODE,
)


class EmbeddingService:
    """
    Real mode:
        sentence-transformers/all-MiniLM-L6-v2

    Fake mode:
        deterministic local hash embeddings for self-test only.
    """

    def __init__(self):
        self.fake_mode = USE_FAKE_MODE

        if self.fake_mode:
            self.dimension = 128
            self.model = None
            return

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Run: pip install -r requirements.txt"
            ) from exc

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        self.dimension = (
            self.model.get_sentence_embedding_dimension()
        )


    def _fake_embed(self, text: str):
        vector = np.zeros(
            self.dimension,
            dtype="float32"
        )

        for token in text.lower().split():
            digest = hashlib.sha256(
                token.encode("utf-8")
            ).digest()

            index = int.from_bytes(
                digest[:4],
                "little",
            ) % self.dimension

            vector[index] += 1.0

        norm = np.linalg.norm(vector)

        if norm > 0:
            vector = vector / norm

        return vector.astype("float32")


    def embed(self, text: str):
        if self.fake_mode:
            return self._fake_embed(text)

        vector = self.model.encode(
            [text]
        )[0]

        return np.asarray(
            vector,
            dtype="float32",
        )


embedding_service = EmbeddingService()
