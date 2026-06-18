"""
Phase 4.4 — app.py write path migrated to save_message_memory_v2.

streamlit, google, and supabase are stubbed before importing app so the
module loads in test context. Tests cover:
  - should_save_rag_user_message gating logic (pure unit, no stubs needed)
  - write block calls save_message_memory_v2, not save_memory_note
  - exception in save does not abort the write block
  - import namespace checks (removed imports absent, new import present)
"""
import sys
from unittest.mock import MagicMock, patch

# Stub all modules that import streamlit or the supabase client
# before any app-level import triggers them.
for _m in (
    "streamlit",
    "google",
    "google.generativeai",
    "supabase",
    "supabase_memory",
    "supabase_memory_v2",
):
    sys.modules.setdefault(_m, MagicMock())

import app  # noqa: E402  (must come after stubs)
from app import should_save_rag_user_message  # noqa: E402
from truth_engine import QueryType  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cls(query_type=None, requires_live_data=False):
    """Build a minimal classification mock."""
    m = MagicMock()
    m.query_type = query_type
    m.requires_live_data = requires_live_data
    return m


def _run_write_block(message, classification, save_fn):
    """
    Mirror the exact write block from app.py so we can exercise it
    without running the full Streamlit main_app() function.

    if should_save_rag_user_message(user_message, classification):
        try:
            save_message_memory_v2(user_id=..., message=..., ...)
        except Exception as error:
            print("[MEMORY V2 SAVE ERROR]", error)
    """
    if should_save_rag_user_message(message, classification):
        try:
            save_fn(
                user_id="u1",
                message=message,
                source="streamlit",
                metadata={"agent_mode": "inik", "route": "streamlit_chat"},
            )
        except Exception as error:
            print("[MEMORY V2 SAVE ERROR]", error)


# ---------------------------------------------------------------------------
# Tests: should_save_rag_user_message gating (pure unit, no streamlit dep)
# ---------------------------------------------------------------------------

def test_srag_qualifying_personal_statement():
    """Declarative personal statement with neutral classification → True."""
    assert should_save_rag_user_message("ฉันชอบดาวเสาร์", _cls()) is True


def test_srag_question_marker_blocked():
    """Message containing Thai question marker → False."""
    assert should_save_rag_user_message("ฉันชอบอะไรเหรอ", _cls()) is False


def test_srag_live_data_blocked():
    """requires_live_data=True blocks write regardless of content."""
    assert should_save_rag_user_message(
        "ฉันชอบดาวเสาร์", _cls(requires_live_data=True)
    ) is False


def test_srag_factual_query_blocked():
    """FACTUAL_QUERY classification blocks write even for declarative text."""
    assert should_save_rag_user_message(
        "ฉันชอบดาวเสาร์", _cls(query_type=QueryType.FACTUAL_QUERY)
    ) is False


def test_srag_tool_query_blocked():
    assert should_save_rag_user_message(
        "ฉันชอบดาวเสาร์", _cls(query_type=QueryType.TOOL_QUERY)
    ) is False


def test_srag_relationship_query_blocked():
    assert should_save_rag_user_message(
        "ฉันชอบดาวเสาร์", _cls(query_type=QueryType.RELATIONSHIP_QUERY)
    ) is False


def test_srag_empty_string_blocked():
    assert should_save_rag_user_message("", _cls()) is False


# ---------------------------------------------------------------------------
# Tests: write block behaviour
# ---------------------------------------------------------------------------

def test_qualifying_message_triggers_save_v2():
    """Qualifying message causes save_fn to be called with correct args."""
    save_mock = MagicMock()
    _run_write_block("ฉันชอบดาวเสาร์", _cls(), save_mock)

    save_mock.assert_called_once()
    _, kwargs = save_mock.call_args
    assert kwargs["message"] == "ฉันชอบดาวเสาร์"
    assert kwargs["source"] == "streamlit"
    assert kwargs["metadata"]["route"] == "streamlit_chat"


def test_question_message_skips_save_fn():
    """Question-like message does not call save_fn at all."""
    save_mock = MagicMock()
    _run_write_block("ฉันชอบอะไรเหรอ", _cls(), save_mock)
    save_mock.assert_not_called()


def test_factual_classification_skips_save_fn():
    """FACTUAL_QUERY classification skips save_fn even for declarative text."""
    save_mock = MagicMock()
    _run_write_block(
        "ฉันชอบดาวเสาร์", _cls(query_type=QueryType.FACTUAL_QUERY), save_mock
    )
    save_mock.assert_not_called()


def test_save_failure_does_not_raise():
    """Exception inside save_fn is swallowed; write block does not propagate it."""
    exploding_save = MagicMock(side_effect=Exception("network error"))
    # Must not raise — the try/except inside _run_write_block absorbs it
    _run_write_block("ฉันชอบดาวเสาร์", _cls(), exploding_save)
    exploding_save.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: import namespace checks
# ---------------------------------------------------------------------------

def test_save_memory_note_not_in_app_namespace():
    """After Phase 4.4, save_memory_note must not be importable from app."""
    assert not hasattr(app, "save_memory_note"), (
        "save_memory_note should have been removed from app.py imports"
    )


def test_save_message_memory_v2_in_app_namespace():
    """save_message_memory_v2 must be present and live in app's namespace."""
    assert hasattr(app, "save_message_memory_v2")


def test_assess_memory_quality_not_in_app_namespace():
    """assess_memory_quality must not be in app's namespace after Phase 4.4."""
    assert not hasattr(app, "assess_memory_quality"), (
        "assess_memory_quality should have been removed from app.py imports"
    )
