"""Deep Agents: parent + two real model-powered subagents, skills, memory and HITL."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from setup_data import initialize, WORKSPACE
from tools import search_docs, search_database, send_email, delete_file

load_dotenv()

class ResearchReport(BaseModel):
    summary: str = Field(description="Short factual summary")
    key_findings: list[str] = Field(description="Verified key findings")
    sources: list[str] = Field(description="Actual filenames or database used")
    confidence: str = Field(description="low, medium, or high")

@dataclass
class UserContext:
    user_id: str
    role: str


def build_agent(model_name: str | None = None):
    key = os.getenv('OPENAI_API_KEY', '').strip()
    if not key or key.startswith('sk-your'):
        raise RuntimeError('Set a real OPENAI_API_KEY in .env before starting research.')
    initialize()
    model = 'openai:' + (model_name or os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'))
    subagents = [
        dict(name='researcher', description='Research local documents and database',
             system_prompt='Use the tools to collect real local evidence. Never invent citations.',
             tools=[search_docs, search_database], model=model),
        dict(name='analyst', description='Compare findings and identify conclusions',
             system_prompt='Analyze evidence and clearly distinguish source facts from interpretation.',
             tools=[search_database], model=model),
    ]
    return create_deep_agent(
        model=model,
        tools=[search_docs, search_database, send_email, delete_file],
        subagents=subagents,
        system_prompt=(
            'You are a technical research agent. For substantial research use researcher and analyst. '
            'Use only actual evidence from local files and SQLite. Do not imply live web access. '
            'When appropriate, use available skills. Never send an email or delete a document '
            'unless the user expressly requests it. Email is local outbox only. '
            'Return a concise structured report.'
        ),
        backend=FilesystemBackend(root_dir=WORKSPACE, virtual_mode=True),
        skills=['/skills/'],
        memory=['/memory/AGENTS.md'],
        interrupt_on={'send_email': True, 'delete_file': True},
        response_format=ResearchReport,
        context_schema=UserContext,
        checkpointer=InMemorySaver(),
        store=InMemoryStore(),
        name='research_agent',
    )
