"""Create real, searchable local sample documents and SQLite rows."""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT / "workspace"
DOCS = WORKSPACE / "docs"
DATABASE = WORKSPACE / "company.db"


def initialize():
    DOCS.mkdir(parents=True, exist_ok=True)
    examples = {
        "langchain.txt": "LangChain supplies model integrations, tools and building blocks for LLM apps.\n",
        "langgraph.txt": "LangGraph supports stateful agent orchestration, checkpoints and human interrupts.\n",
        "deepagents.txt": "Deep Agents is an agent harness with planning, subagents, skills and filesystem tooling.\n",
    }
    for filename, content in examples.items():
        path = DOCS / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    with sqlite3.connect(DATABASE) as db:
        db.execute("CREATE TABLE IF NOT EXISTS records (topic TEXT PRIMARY KEY, detail TEXT NOT NULL)")
        db.executemany("INSERT OR IGNORE INTO records VALUES (?, ?)", [
            ("LangChain", "Provides model and tool abstractions"),
            ("LangGraph", "Provides stateful workflows and checkpoints"),
            ("Deep Agents", "Provides subagents and filesystem-supported agent harness"),
        ])

if __name__ == "__main__":
    initialize()
    print("Workspace initialized:", WORKSPACE)
