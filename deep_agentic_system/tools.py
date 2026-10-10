"""Actual local search tools; external email is intentionally NOT sent."""
from pathlib import Path
import sqlite3
import uuid
from langchain.tools import tool
from setup_data import DOCS, DATABASE, WORKSPACE


def _terms(query: str):
    import re
    return [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) >= 3]

@tool
def search_docs(query: str) -> str:
    """Search the demo's actual .txt/.md documents. Returns filename and matching lines."""
    words = _terms(query)
    if not words:
        return "Please supply a longer search phrase."
    found = []
    for p in sorted(DOCS.glob('*')):
        if not p.is_file() or p.suffix.lower() not in {'.txt', '.md'}:
            continue
        for number, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
            if any(t in line.lower() for t in words):
                found.append(f"{p.name}:{number} {line[:500]}")
    return "\n".join(found[:25]) or "No matches in local documents."

@tool
def search_database(query: str) -> str:
    """Search the local SQLite company database for matching topics/details."""
    words = _terms(query)
    if not words:
        return "Please supply a longer search phrase."
    with sqlite3.connect(DATABASE) as db:
        rows = db.execute("SELECT topic, detail FROM records").fetchall()
    found = [f"{topic}: {detail}" for topic, detail in rows
             if any(t in (topic + ' ' + detail).lower() for t in words)]
    return "\n".join(found[:25]) or "No matches in local database."

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Save an email in local demo outbox; does NOT send an external email. Requires approval."""
    outbox = WORKSPACE / 'outbox'
    outbox.mkdir(parents=True, exist_ok=True)
    file = outbox / f'{uuid.uuid4().hex}.txt'
    file.write_text(f'To: {to}\nSubject: {subject}\n\n{body}', encoding='utf-8')
    return f"Saved demo email in {file.relative_to(WORKSPACE)}. Nothing sent externally."

@tool
def delete_file(path: str) -> str:
    """Delete an ordinary document in workspace/docs, ONLY after human approval."""
    safe_folder = DOCS.resolve()
    candidate = (safe_folder / Path(path).name).resolve()
    if candidate.parent != safe_folder or candidate.suffix.lower() not in ('.txt', '.md'):
        return 'Denied: only workspace/docs/*.txt or *.md can be deleted.'
    if not candidate.is_file():
        return 'File does not exist.'
    candidate.unlink()
    return f'Deleted {candidate.name} from demo docs.'
