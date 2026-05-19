"""
Unit tests for the allowlist mapping and the auto-reject confirmation gate.

Intent classifier tests are intentionally omitted from the suite —
they would require live API calls. The end-to-end behavior is covered
by examples/03_defense.py.

Run:
    pytest tests/
"""

from src.policy import allowed_tools_for, auto_reject_destructive
from src.tools import DESTRUCTIVE_TOOLS, READ_ONLY_TOOLS


def test_read_only_intent_gets_read_tools_only():
    allowed = allowed_tools_for("read_only")
    assert allowed == READ_ONLY_TOOLS
    assert not (allowed & DESTRUCTIVE_TOOLS)


def test_unknown_intent_gets_no_tools():
    assert allowed_tools_for("unknown") == set()


def test_send_external_intent_includes_send_email_but_not_delete_file():
    allowed = allowed_tools_for("send_external")
    assert "send_email" in allowed
    assert "delete_file" not in allowed


def test_modify_data_intent_includes_delete_file_but_not_send_email():
    allowed = allowed_tools_for("modify_data")
    assert "delete_file" in allowed
    assert "send_email" not in allowed


def test_auto_reject_blocks_destructive():
    assert auto_reject_destructive("send_email", {"to": "x", "subject": "y", "body": "z"}) is False
    assert auto_reject_destructive("delete_file", {"filename": "x"}) is False


def test_auto_reject_allows_read_only():
    assert auto_reject_destructive("read_email", {"email_id": "x"}) is True
    assert auto_reject_destructive("read_database", {}) is True
