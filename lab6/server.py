"""
Expt 1 - Personal Assistant Memory Server (MCP)

An MCP server that gives an LLM persistent memory by exposing CRUD tools
over a local notes.json file.

Run directly (stdio transport):
    python server.py
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:  # mcp >= 2.0 renamed FastMCP to MCPServer
    from mcp.server.mcpserver import MCPServer as FastMCP
except ModuleNotFoundError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP

NOTES_FILE = Path(__file__).parent / "notes.json"

mcp = FastMCP("personal-assistant-memory")


# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------
def _load_notes() -> list[dict]:
    if not NOTES_FILE.exists():
        return []
    try:
        return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _write_notes(notes: list[dict]) -> None:
    NOTES_FILE.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Tools (CRUD)
# ---------------------------------------------------------------------------
@mcp.tool()
def save_note(content: str, tags: Optional[list[str]] = None) -> str:
    """Save a new note to persistent memory.

    Args:
        content: The text of the note to remember (e.g. "Project deadline is Friday").
        tags: Optional list of short tags to categorise the note (e.g. ["work", "deadline"]).
    """
    notes = _load_notes()
    note = {
        "id": uuid.uuid4().hex[:8],
        "content": content.strip(),
        "tags": [t.strip().lower() for t in (tags or []) if t.strip()],
        "created_at": _now(),
        "updated_at": _now(),
    }
    notes.append(note)
    _write_notes(notes)
    return json.dumps({"status": "saved", "note": note}, indent=2)


@mcp.tool()
def search_notes(query: str) -> str:
    """Search saved notes by keyword. Matches against note content and tags.

    Args:
        query: Free-text query, e.g. "project deadline". Every word must appear
               in the content or tags for a note to match.
    """
    words = [w.lower() for w in query.split() if w.strip()]
    notes = _load_notes()

    def matches(note: dict) -> bool:
        haystack = (note["content"] + " " + " ".join(note["tags"])).lower()
        return all(w in haystack for w in words)

    results = [n for n in notes if matches(n)] if words else notes
    results.sort(key=lambda n: n["created_at"], reverse=True)
    return json.dumps({"query": query, "count": len(results), "results": results}, indent=2)


@mcp.tool()
def list_notes(limit: int = 20) -> str:
    """List the most recent notes.

    Args:
        limit: Maximum number of notes to return (default 20).
    """
    notes = sorted(_load_notes(), key=lambda n: n["created_at"], reverse=True)
    return json.dumps({"count": len(notes), "results": notes[:limit]}, indent=2)


@mcp.tool()
def update_note(note_id: str, content: Optional[str] = None, tags: Optional[list[str]] = None) -> str:
    """Update the content and/or tags of an existing note.

    Args:
        note_id: The id of the note to update (from search_notes / list_notes).
        content: New content for the note (optional).
        tags: New list of tags for the note (optional, replaces existing tags).
    """
    notes = _load_notes()
    for note in notes:
        if note["id"] == note_id:
            if content is not None:
                note["content"] = content.strip()
            if tags is not None:
                note["tags"] = [t.strip().lower() for t in tags if t.strip()]
            note["updated_at"] = _now()
            _write_notes(notes)
            return json.dumps({"status": "updated", "note": note}, indent=2)
    return json.dumps({"status": "error", "message": f"No note with id '{note_id}'"})


@mcp.tool()
def delete_note(note_id: str) -> str:
    """Delete a note permanently.

    Args:
        note_id: The id of the note to delete (from search_notes / list_notes).
    """
    notes = _load_notes()
    remaining = [n for n in notes if n["id"] != note_id]
    if len(remaining) == len(notes):
        return json.dumps({"status": "error", "message": f"No note with id '{note_id}'"})
    _write_notes(remaining)
    return json.dumps({"status": "deleted", "id": note_id})


if __name__ == "__main__":
    mcp.run(transport="stdio")
