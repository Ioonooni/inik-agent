"""
Phase 4.5 — get_recent_memories wired into runtime recall.

Tests:
  - get_recent_memories returns [] for empty user_id
  - get_recent_memories returns results from list_recent_memories_v2
  - get_recent_memories returns [] on exception (never raises)
  - recall_memories includes a recent memory not already in raw_memories
  - recall_memories dedupes memory already present in raw_memories by memory_id
  - app imports get_recent_memories from rag_prompt
"""
import sys
from unittest.mock import MagicMock, patch

# Stub all modules not available in the test interpreter before any import
for _m in (
    "streamlit",
    "google",
    "google.generativeai",
    "supabase",
    "supabase_memory",
    "supabase_memory_v2",
    "requests",       # not available in the bare-pytest interpreter
    "event_logger",   # imports requests at module level
):
    sys.modules.setdefault(_m, MagicMock())

import app  # noqa: E402 — must come after stubs
from rag_prompt import get_recent_memories  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mem(content, importance=80, *, memory_id=None, user_id="u1") -> dict:
    return {
        "memory_id": memory_id or f"id_{abs(hash(content)):010}",
        "user_id": user_id,
        "content": content,
        "memory_type": "user_fact",
        "importance": importance,
        "hit_count": 1,
        "last_seen_at": "2026-06-17T12:00:00+00:00",
        "metadata": {},
    }


def _recent_result(memories: list) -> dict:
    return {"ok": True, "backend": "memories_v2", "results": memories}


# ---------------------------------------------------------------------------
# Tests: get_recent_memories
# ---------------------------------------------------------------------------

def test_get_recent_memories_empty_user_id():
    """Empty user_id must short-circuit and return [] without calling the gateway."""
    assert get_recent_memories("") == []
    assert get_recent_memories(None) == []


def test_get_recent_memories_returns_results():
    """Passes results from list_recent_memories_v2 through unchanged."""
    memories = [_mem("ฉันชอบดาวเสาร์"), _mem("ฉันชอบดาวพฤหัส")]

    with patch("rag_prompt.list_recent_memories_v2", return_value=_recent_result(memories)):
        result = get_recent_memories("u1", limit=5)

    assert result == memories


def test_get_recent_memories_returns_empty_on_exception():
    """Exception inside list_recent_memories_v2 must be swallowed; returns []."""
    with patch("rag_prompt.list_recent_memories_v2",
               side_effect=Exception("gateway down")):
        result = get_recent_memories("u1")

    assert result == []


# ---------------------------------------------------------------------------
# Tests: recall_memories dedup logic (mirrors the block in app.py)
# ---------------------------------------------------------------------------

def _build_recall(raw_memories: list, recent_memories: list) -> list:
    """Mirror the exact recall_memories block from app.py."""
    recall_memories = list(raw_memories or [])
    try:
        seen_ids = {m.get("memory_id") for m in recall_memories if m.get("memory_id")}
        for m in recent_memories:
            if m.get("memory_id") not in seen_ids:
                recall_memories.append(m)
    except Exception:
        pass
    return recall_memories


def test_recall_includes_new_recent_memory():
    """Recent memory with unseen memory_id is appended to recall_memories."""
    raw = [_mem("ฉันชื่อนิค", memory_id="id_name")]
    recent = [_mem("ฉันชอบดาวเสาร์", memory_id="id_saturn")]

    result = _build_recall(raw, recent)

    assert len(result) == 2
    ids = {m["memory_id"] for m in result}
    assert "id_name" in ids
    assert "id_saturn" in ids


def test_recall_dedupes_memory_id_already_present():
    """Recent memory whose memory_id is already in raw_memories is not duplicated."""
    shared = _mem("ฉันชอบดาวเสาร์", memory_id="id_saturn")
    raw = [shared]
    recent = [dict(shared)]  # same memory_id, different dict instance

    result = _build_recall(raw, recent)

    assert len(result) == 1
    assert result[0]["memory_id"] == "id_saturn"


# ---------------------------------------------------------------------------
# Tests: import namespace
# ---------------------------------------------------------------------------

def test_app_imports_get_recent_memories():
    """get_recent_memories must be importable from app's namespace (Phase 4.5)."""
    assert hasattr(app, "get_recent_memories")
