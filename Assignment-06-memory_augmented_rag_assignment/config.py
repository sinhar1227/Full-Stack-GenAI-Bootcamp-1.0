import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

MAX_RECENT_MESSAGES = int(
    os.getenv("MAX_RECENT_MESSAGES", "6")
)

TOP_K_DOCUMENTS = int(
    os.getenv("TOP_K_DOCUMENTS", "3")
)

TOP_K_MEMORIES = int(
    os.getenv("TOP_K_MEMORIES", "3")
)

LONG_TERM_DB_PATH = os.getenv(
    "LONG_TERM_DB_PATH",
    str(BASE_DIR / "long_term_memory.db"),
)

USE_FAKE_MODE = os.getenv(
    "USE_FAKE_MODE",
    "0",
) == "1"
