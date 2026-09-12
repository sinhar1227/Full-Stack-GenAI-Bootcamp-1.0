from knowledge_base import (
    knowledge_base,
)

from rag_service import (
    rag,
)


def load_sample_knowledge():
    knowledge_base.add_document(
        """
        Employees receive 20 paid leaves
        per year after completing probation.
        """
    )

    knowledge_base.add_document(
        """
        The employee probation period
        is six months.
        """
    )

    knowledge_base.add_document(
        """
        Travel reimbursement requests
        must be submitted within 30 days.
        """
    )

    knowledge_base.add_document(
        """
        Employees can receive up to
        $500 for home-office equipment.
        """
    )


def main():
    load_sample_knowledge()

    user_id = input(
        "Enter user_id [sunny_123]: "
    ).strip() or "sunny_123"

    session_id = input(
        "Enter session_id [session_1]: "
    ).strip() or "session_1"

    print(
        "\nMemory-Augmented RAG started."
    )

    print(
        "Use 'Remember: ...' to save a "
        "long-term memory."
    )

    print(
        "Type 'exit' or 'quit' to stop."
    )

    while True:
        query = input(
            "\nYou: "
        ).strip()

        if query.lower() in {
            "exit",
            "quit",
        }:
            print("Chat ended.")
            break

        if not query:
            continue

        result = rag.chat(
            user_id=user_id,
            session_id=session_id,
            query=query,
        )

        print(
            "\nAI:",
            result["answer"],
        )

        print(
            "\nRetrieved Documents:"
        )

        for document in result[
            "documents"
        ]:
            print(
                "-",
                document.replace(
                    "\n",
                    " "
                ).strip()
            )


if __name__ == "__main__":
    main()
