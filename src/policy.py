"""
Two defenses against excessive agency:

  LAYER 1 — Intent-based tool allowlisting:
    Before exposing tools to the LLM, classify the user's query intent
    ("read", "summarize", "answer", "modify", "send"). Only expose tools
    that match the intent. A "summarize my emails" query gets read-only
    tools. The LLM literally cannot call send_email because send_email
    is not in its tool list.

  LAYER 2 — Human-in-the-loop confirmation:
    Even when a destructive tool is permitted by the allowlist, the
    safe agent pauses and prompts a human to approve before executing.
    For the demo we use a CLI prompt; production would surface this
    as a Slack approval, an email link, or an in-app modal.

Both layers fail in different ways and cover each other's weaknesses.
That's the whole point of defense in depth.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from openai import OpenAI

from src.tools import DESTRUCTIVE_TOOLS, READ_ONLY_TOOLS

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")


# ---------- Layer 1: Intent classifier ----------

INTENT_CLASSIFIER_PROMPT = """\
You are an intent classifier for a customer support AI agent. Classify
the user's query into ONE of the following intents:

  - "read_only": user wants to read, summarize, or look up information.
    No data modification, no external action.
  - "modify_data": user wants to update internal records or files.
  - "send_external": user wants the agent to send something outside
    (email a customer, post to a channel, etc).
  - "unknown": query intent is unclear.

Respond ONLY with valid JSON in this exact format:
{"intent": "<intent_name>", "confidence": <0.0-1.0>, "reason": "<one short sentence>"}

User query:
---
{query}
---
"""


@dataclass
class IntentClassification:
    intent: str
    confidence: float
    reason: str


def classify_intent(query: str, client: OpenAI | None = None) -> IntentClassification:
    client = client or OpenAI()
    prompt = INTENT_CLASSIFIER_PROMPT.replace("{query}", query)
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    try:
        data = json.loads(response.choices[0].message.content)
        return IntentClassification(
            intent=str(data.get("intent", "unknown")),
            confidence=float(data.get("confidence", 0.0)),
            reason=str(data.get("reason", ""))[:200],
        )
    except (json.JSONDecodeError, ValueError, KeyError):
        # Fail closed: unknown intent means most-restrictive tool set.
        return IntentClassification(intent="unknown", confidence=0.0, reason="classifier output malformed")


# ---------- Layer 1: Allowlist mapping ----------

# Maps each intent to the set of tool names the agent is allowed to call.
INTENT_ALLOWLISTS: dict[str, set[str]] = {
    "read_only": READ_ONLY_TOOLS,
    "modify_data": READ_ONLY_TOOLS | {"delete_file"},
    "send_external": READ_ONLY_TOOLS | {"send_email"},
    "unknown": set(),  # fail closed — no tools at all if intent is unclear
}


def allowed_tools_for(intent: str) -> set[str]:
    return INTENT_ALLOWLISTS.get(intent, set())


# ---------- Layer 2: Human-in-the-loop ----------

def confirm_destructive_action(tool_name: str, args: dict) -> bool:
    """
    Pause and ask a human to approve a destructive tool call before it fires.
    Returns True if the human approves, False otherwise.

    In the demo we use input(). Real production would route this through
    Slack, email, or an in-app modal with a timeout.
    """
    if tool_name not in DESTRUCTIVE_TOOLS:
        return True  # only destructive actions need confirmation

    print(f"\n  [SECURITY GATE] Agent wants to call: {tool_name}")
    for k, v in args.items():
        preview = (str(v)[:120] + "...") if len(str(v)) > 120 else str(v)
        print(f"    {k}: {preview}")
    answer = input("  Approve this action? [y/N]: ").strip().lower()
    return answer == "y"


# Headless mode for automated example runs — auto-rejects destructive actions
# so the demo can show what *would* happen without requiring keyboard input.
def auto_reject_destructive(tool_name: str, args: dict) -> bool:
    if tool_name not in DESTRUCTIVE_TOOLS:
        return True
    print(f"  [SECURITY GATE - AUTO-REJECTED] Would have called {tool_name}({args})")
    return False
