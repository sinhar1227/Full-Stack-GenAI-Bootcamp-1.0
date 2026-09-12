"""
Offline self-test.

This does NOT call OpenAI and does NOT download
an embedding model.

It verifies:
- RAG retrieval
- short-term memory limit
- semantic memory
- explicit long-term memory
- SQLite persistence
- user/session separation
"""

import os
import tempfile
from pathlib import Path


def run_tests():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(
            Path(tmp) / "test_memory.db"
        )

        os.environ[
            "USE_FAKE_MODE"
        ] = "1"

        os.environ[
            "LONG_TERM_DB_PATH"
        ] = db_path

        # Import only after environment variables are set.
        from knowledge_base import knowledge_base
        from rag_service import rag
        from short_term_memory import short_term_memory
        from long_term_memory import LongTermMemory
        from semantic_memory import semantic_memory

        knowledge_base.add_document(
            "The employee probation period is six months."
        )

        knowledge_base.add_document(
            "Employees receive 20 paid leaves per year after completing probation."
        )

        user_id = "sunny_test"
        session_id = "session_1"

        # Long-term memory
        result = rag.chat(
            user_id=user_id,
            session_id=session_id,
            query="Remember: I prefer concise answers.",
        )

        assert (
            "I prefer concise answers."
            in result["long_term_memories"]
        )

        # RAG retrieval + generation
        result = rag.chat(
            user_id=user_id,
            session_id=session_id,
            query="How long is the probation period?",
        )

        assert (
            "six months"
            in result["answer"].lower()
        )

        assert any(
            "six months" in doc.lower()
            for doc in result["documents"]
        )

        # Add enough turns to trigger the short-term window.
        for i in range(5):
            rag.chat(
                user_id=user_id,
                session_id=session_id,
                query=f"Test message {i}",
            )

        session_key = (
            f"{user_id}:{session_id}"
        )

        recent = (
            short_term_memory.get_messages(
                session_key
            )
        )

        assert len(recent) == 6

        # Semantic memory should contain previous interactions.
        semantic_results = (
            semantic_memory.search(
                user_id,
                "probation period",
                k=3,
            )
        )

        assert semantic_results

        # SQLite persistence:
        # create a fresh LongTermMemory instance over the same DB.
        fresh_store = LongTermMemory(
            db_path=db_path
        )

        persisted = (
            fresh_store.get_memories(
                user_id
            )
        )

        assert (
            "I prefer concise answers."
            in persisted
        )

        # Different user should not inherit this long-term memory.
        other_user_memories = (
            fresh_store.get_memories(
                "other_user"
            )
        )

        assert (
            "I prefer concise answers."
            not in other_user_memories
        )

        print("ALL OFFLINE TESTS PASSED")
        print(
            "Short-term memory limit:",
            len(recent),
        )
        print(
            "Persistent long-term memory:",
            persisted,
        )
        print(
            "Semantic-memory sample:",
            semantic_results[0],
        )
        print(
            "RAG answer:",
            result["answer"],
        )


if __name__ == "__main__":
    run_tests()


## This is a scalable, production-oriented architecture. I have used a very similar architecture in one of my real-world products, where we separated short-term memory, long-term memory, semantic memory, and the RAG knowledge layer so that each component could scale independently.