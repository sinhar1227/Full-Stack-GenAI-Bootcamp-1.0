from config import (
    TOP_K_DOCUMENTS,
    TOP_K_MEMORIES,
)

from short_term_memory import (
    short_term_memory,
)

from long_term_memory import (
    long_term_memory,
)

from semantic_memory import (
    semantic_memory,
)

from knowledge_base import (
    knowledge_base,
)

from llm_service import (
    llm_service,
)


class MemoryAugmentedRAG:

    @staticmethod
    def _format_messages(
        messages,
    ):
        if not messages:
            return "No recent conversation."

        return "\n".join(
            f"{message['role']}: "
            f"{message['content']}"
            for message in messages
        )


    @staticmethod
    def _format_list(
        values,
    ):
        if not values:
            return "None."

        return "\n".join(
            f"- {value}"
            for value in values
        )


    @staticmethod
    def _extract_explicit_memory(
        query: str,
    ):
        prefix = "remember:"

        if not query.lower().startswith(
            prefix
        ):
            return None

        memory = query[
            len(prefix):
        ].strip()

        return memory or None


    def chat(
        self,
        user_id: str,
        session_id: str,
        query: str,
    ):
        session_key = (
            f"{user_id}:{session_id}"
        )

        # 1. Read short-term conversation memory
        recent_messages = (
            short_term_memory.get_messages(
                session_key
            )
        )

        # 2. Read persistent long-term user memory
        long_term_memories = (
            long_term_memory.get_memories(
                user_id
            )
        )

        # 3. Retrieve semantically relevant past interactions
        relevant_memories = (
            semantic_memory.search(
                user_id,
                query,
                TOP_K_MEMORIES,
            )
        )

        # 4. Retrieve relevant RAG documents
        relevant_documents = (
            knowledge_base.search(
                query,
                TOP_K_DOCUMENTS,
            )
        )

        # 5. Build final context
        prompt = f"""
You are a helpful AI assistant.

Use memory only for conversation continuity
and personalization.

Use retrieved knowledge for factual domain
information.

------------------------------
RECENT CONVERSATION
------------------------------
{self._format_messages(recent_messages)}

------------------------------
LONG-TERM USER MEMORY
------------------------------
{self._format_list(long_term_memories)}

------------------------------
RELEVANT PAST MEMORIES
------------------------------
{self._format_list(relevant_memories)}

------------------------------
RETRIEVED KNOWLEDGE
------------------------------
{self._format_list(relevant_documents)}

------------------------------
CURRENT QUESTION
------------------------------
{query}

Answer the current question.

If factual information is required but is not
available in the retrieved knowledge, say that
you do not know based on the available knowledge.
""".strip()

        # 6. Generate answer
        answer = llm_service.generate(
            prompt
        )

        # 7. Update short-term memory
        short_term_memory.add_message(
            session_key,
            "user",
            query,
        )

        short_term_memory.add_message(
            session_key,
            "assistant",
            answer,
        )

        # 8. Update semantic memory
        semantic_memory.add_memory(
            user_id,
            (
                f"User: {query}\n"
                f"Assistant: {answer}"
            )
        )

        # 9. Save explicit long-term memory
        new_long_term_memory = (
            self._extract_explicit_memory(
                query
            )
        )

        if new_long_term_memory:
            long_term_memory.add_memory(
                user_id,
                new_long_term_memory,
            )

        return {
            "answer": answer,
            "documents": relevant_documents,
            "semantic_memories": relevant_memories,
            "long_term_memories": (
                long_term_memory.get_memories(
                    user_id
                )
            ),
            "recent_messages": (
                short_term_memory.get_messages(
                    session_key
                )
            ),
        }


rag = MemoryAugmentedRAG()
