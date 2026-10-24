import math
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from mcp.server import MCPServer

load_dotenv()

server = MCPServer("Company Policy MCP Server")

##Data Source to Vector Database(in real time)
POLICY_DOCS = [
    {
        "id": "flight-policy",
        "text": (
            "For company trips under 8 hours, employees must book economy class. "
            "Business class requires director approval."
        ),
    },
    {
        "id": "hotel-policy",
        "text": (
            "Employees may normally book hotels up to 4-star category. "
            "The standard international hotel budget is ₹12,000 per night."
        ),
    },
    {
        "id": "expense-policy",
        "text": (
            "Flight, hotel, airport taxi, and approved local transport expenses "
            "are reimbursable when valid receipts are submitted."
        ),
    },
    {
        "id": "leave-policy",
        "text": (
            "Planned leave should normally be submitted at least 7 days in advance."
        ),
    },
]

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


@lru_cache(maxsize=1)
def _document_vectors() -> tuple[tuple[float, ...], ...]:
    vectors = embeddings.embed_documents(
        [doc["text"] for doc in POLICY_DOCS]
    )
    return tuple(tuple(vector) for vector in vectors)


# ============================================================
# RAG TOOL = DYNAMIC RETRIEVAL
# ============================================================

@server.tool()
def search_company_policy(
    query: str,
    top_k: int = 2,
) -> list[dict]:
    """Semantic search over company policy documents."""

    query_vector = embeddings.embed_query(query)
    vectors = _document_vectors()

    scored = []

    for doc, vector in zip(POLICY_DOCS, vectors):
        score = _cosine_similarity(
            query_vector,
            list(vector),
        )

        scored.append(
            {
                "id": doc["id"],
                "text": doc["text"],
                "score": round(score, 4),
            }
        )

    scored.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    top_k = max(1, min(top_k, len(scored)))
    return scored[:top_k]


# ============================================================
# RESOURCE = KNOWN/FIXED POLICY SUMMARY
# ============================================================

@server.resource("policy://travel-summary")
def travel_policy_summary() -> str:
    """Readable policy summary exposed as a Resource."""
    return """
Company travel summary:
- Economy class is required for trips under 8 hours unless director-approved.
- Hotels should normally be 4-star or below.
- Standard international hotel budget: ₹12,000/night.
- Valid receipts are required for reimbursement.
""".strip()


if __name__ == "__main__":
    server.run()
