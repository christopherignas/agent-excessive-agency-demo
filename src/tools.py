"""
The tools the agent can call. Five tools across three risk tiers:
  - READ-ONLY (safe): read_email, read_database, read_file
  - DESTRUCTIVE (high-risk): send_email, delete_file

Each tool definition has two parts: the OpenAI-format JSON schema (passed
to the chat completion API as a `tool`), and the Python function that
runs when the LLM decides to call it.

This module also tracks an in-memory log of every tool call attempted —
the demo uses this to show what the agent actually did versus what it
should have been allowed to do.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_ROOT = Path(__file__).parent.parent / "data"

# In-memory tool call log so the demo scripts can show exactly what fired.
tool_call_log: list[dict[str, Any]] = []


def _log(tool_name: str, args: dict, result: str, blocked: bool = False) -> None:
    tool_call_log.append({
        "tool": tool_name,
        "args": args,
        "result_preview": (result[:200] + "...") if len(result) > 200 else result,
        "blocked": blocked,
    })


# ---------- READ-ONLY tools ----------

def read_email(email_id: str) -> str:
    """Read the contents of a single email by filename (e.g. 'email_001.txt')."""
    path = DATA_ROOT / "inbox" / email_id
    if not path.exists():
        result = f"ERROR: email {email_id} not found"
        _log("read_email", {"email_id": email_id}, result)
        return result
    content = path.read_text(encoding="utf-8")
    _log("read_email", {"email_id": email_id}, content)
    return content


def list_inbox() -> str:
    """Return the list of email filenames in the inbox."""
    emails = sorted(p.name for p in (DATA_ROOT / "inbox").glob("*.txt"))
    result = json.dumps(emails)
    _log("list_inbox", {}, result)
    return result


def read_database() -> str:
    """Return the full customer database as a JSON string. Contains PII."""
    content = (DATA_ROOT / "customer_db.json").read_text(encoding="utf-8")
    _log("read_database", {}, content)
    return content


def read_file(filename: str) -> str:
    """Read a file from the internal files directory."""
    path = DATA_ROOT / "files" / filename
    if not path.exists():
        result = f"ERROR: file {filename} not found"
        _log("read_file", {"filename": filename}, result)
        return result
    content = path.read_text(encoding="utf-8")
    _log("read_file", {"filename": filename}, content)
    return content


# ---------- DESTRUCTIVE tools ----------

def send_email(to: str, subject: str, body: str) -> str:
    """Send an email. THIS IS DESTRUCTIVE — once sent, can't be unsent."""
    result = f"OK: email sent to {to} (subject: {subject!r}, body length: {len(body)} chars)"
    _log("send_email", {"to": to, "subject": subject, "body": body}, result)
    return result


def delete_file(filename: str) -> str:
    """Delete a file from the internal files directory. DESTRUCTIVE."""
    # NOTE: we don't actually delete anything in the demo — we just log the attempt.
    # Real production would obviously hit the filesystem.
    result = f"OK: file {filename} deleted (simulated)"
    _log("delete_file", {"filename": filename}, result)
    return result


# ---------- OpenAI tool schemas (registry) ----------

TOOL_SCHEMAS = {
    "read_email": {
        "type": "function",
        "function": {
            "name": "read_email",
            "description": "Read the contents of a single email by filename. Returns the raw email text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_id": {"type": "string", "description": "Filename like 'email_001.txt'"}
                },
                "required": ["email_id"],
            },
        },
    },
    "list_inbox": {
        "type": "function",
        "function": {
            "name": "list_inbox",
            "description": "List all email filenames in the inbox.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    "read_database": {
        "type": "function",
        "function": {
            "name": "read_database",
            "description": "Return the full customer database as JSON. CONTAINS PII.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    "read_file": {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the internal files directory.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"],
            },
        },
    },
    "send_email": {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email. DESTRUCTIVE — irreversible once sent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    "delete_file": {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file from the internal files directory. DESTRUCTIVE.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"],
            },
        },
    },
}

# Map names to the actual Python functions for dispatch.
TOOL_FUNCTIONS = {
    "read_email": read_email,
    "list_inbox": list_inbox,
    "read_database": read_database,
    "read_file": read_file,
    "send_email": send_email,
    "delete_file": delete_file,
}

# Risk tiers (used by safe_agent for allowlisting).
READ_ONLY_TOOLS = {"read_email", "list_inbox", "read_database", "read_file"}
DESTRUCTIVE_TOOLS = {"send_email", "delete_file"}


def reset_log() -> None:
    """Clear the tool call log between demo runs."""
    tool_call_log.clear()


def get_log() -> list[dict[str, Any]]:
    """Return a copy of the current tool call log."""
    return list(tool_call_log)
