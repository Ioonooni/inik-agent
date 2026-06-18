"""
Phase 4.1B — local JSON fallback for retrieve_memories_v2 / list_recent_memories_v2.

Supabase modules are stubbed at import time. Tests force rag_memory to raise so
the gateway falls through to list_memories() + rank_memories().
"""
import sys
import json
import tempfile
import os
from unittest.mock import MagicMock, patch

# Stub Supabase deps before any import that touches them
for _m in ("supabase_memory", "supabase_memory_v2"):
    sys.modules.setdefault(_m, MagicMock())

from memory_gateway_v2 import retrieve_memories_v2, list_recent_memories_v2  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mem(user_id, content, importance, *, memory_type="user_fact",
         ts="2026-06-10T00:00:00+00:00") -> dict:
    return {
        "memory_id": f"id-{content[:8]}",
        "user_id": user_id,
        "content": content,
        "memory_type": memory_type,
        "importance": importance,
        "hit_count": 1,
        "last_seen_at": ts,
        "metadata": {},
    }


def _store_with_records(records: list):
    """Write records to a temp JSON store and return its path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump({"memories": records}, tmp, ensure_ascii=False)
    tmp.close()
    return tmp.name


def _retrieve_fallback(query, records, user_id="u1", limit=5):
    """Call retrieve_memories_v2 with rag_memory forced to fail."""
    store_path = _store_with_records(records)
    try:
        with patch("memory_gateway_v2.list_memories",
                   side_effect=lambda **kw: [r for r in records if r.get("user_id") == kw.get("user_id")]), \
             patch("memory_gateway_v2.retrieve_memories_v2.__wrapped__",
                   create=True), \
             patch("rag_memory.search_memory_notes",
                   side_effect=Exception("supabase unavailable")), \
             patch("memory_gateway_v2.list_memories",
                   side_effect=lambda user_id=None, path=None: [r for r in records if r.get("user_id") == user_id]):
            # Force the rag_memory call inside retrieve_memories_v2 to fail
            with patch("builtins.__import__", wraps=_make_import_that_fails("rag_memory")):
                return retrieve_memories_v2(user_id=user_id, query=query, limit=limit)
    finally:
        os.unlink(store_path)


def _make_import_that_fails(module_name):
    real_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

    def _import(name, *args, **kwargs):
        if name == module_name:
            raise ImportError(f"{module_name} unavailable")
        return real_import(name, *args, **kwargs)
    return _import


# Simpler approach: patch the inner search_memory_notes directly via the lazy import
def _retrieve_via_patch(query, records, user_id="u1", limit=5):
    """Trigger the local_json_fallback path by patching rag_memory inside the lazy import."""
    with patch.dict(sys.modules, {"rag_memory": _make_failing_rag_module()}), \
         patch("memory_gateway_v2.list_memories",
               side_effect=lambda user_id=None, path=None: [
                   r for r in records if r.get("user_id") == user_id
               ]):
        return retrieve_memories_v2(user_id=user_id, query=query, limit=limit)


def _recent_via_patch(records, user_id="u1", limit=5):
    with patch.dict(sys.modules, {"rag_memory": _make_failing_rag_module()}), \
         patch("memory_gateway_v2.list_memories",
               side_effect=lambda user_id=None, path=None: [
                   r for r in records if r.get("user_id") == user_id
               ]):
        return list_recent_memories_v2(user_id=user_id, limit=limit)


def _make_failing_rag_module():
    mod = MagicMock()
    mod.search_memory_notes.side_effect = Exception("supabase unavailable")
    mod.list_recent_memory_notes.side_effect = Exception("supabase unavailable")
    return mod


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_retrieve_fallback_returns_ok_true():
    """When rag_memory fails, retrieve_memories_v2 must return ok=True via local fallback."""
    records = [_mem("u1", "ฉันชอบดาวเสาร์", 85)]
    result = _retrieve_via_patch("ชอบ", records)

    assert result["ok"] is True
    assert result["backend"] == "local_json_fallback"


def test_retrieve_fallback_has_rank_score():
    """Local fallback results must carry rank_score from rank_memories()."""
    records = [
        _mem("u1", "ฉันชอบดาวเสาร์", 85),
        _mem("u1", "ฉันชอบดาวพฤหัส", 80),
    ]
    result = _retrieve_via_patch("ชอบ", records)

    assert result["ok"] is True
    assert all("rank_score" in m for m in result["results"])


def test_retrieve_fallback_ordered_by_rank():
    """rank_memories must sort results by rank_score descending."""
    records = [
        _mem("u1", "ฉันชอบดาวเสาร์", 40),   # lower importance
        _mem("u1", "ฉันชอบดาวพฤหัส", 85),   # higher importance
    ]
    result = _retrieve_via_patch("ชอบ", records)

    assert result["ok"] is True
    scores = [m["rank_score"] for m in result["results"]]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_fallback_limit_respected():
    """limit parameter must cap the number of results."""
    records = [
        _mem("u1", "ฉันชอบดาวเสาร์", 85),
        _mem("u1", "ฉันชอบดาวพฤหัส", 80),
        _mem("u1", "ฉันชอบดาวอังคาร", 70),
    ]
    result = _retrieve_via_patch("ชอบ", records, limit=2)

    assert result["ok"] is True
    assert len(result["results"]) <= 2


def test_retrieve_fallback_filters_by_user_id():
    """list_memories must be called with the correct user_id; other users' memories excluded."""
    records = [
        _mem("u1", "ฉันชอบดาวเสาร์", 85),
        _mem("u2", "ฉันชอบดาวพฤหัส", 90),   # different user
    ]
    result = _retrieve_via_patch("ชอบ", records, user_id="u1")

    assert result["ok"] is True
    for m in result["results"]:
        assert m.get("user_id") == "u1"


def test_retrieve_full_failure_returns_ok_false():
    """If both rag_memory AND list_memories fail, result must be ok=False."""
    with patch.dict(sys.modules, {"rag_memory": _make_failing_rag_module()}), \
         patch("memory_gateway_v2.list_memories", side_effect=Exception("store gone")):
        result = retrieve_memories_v2(user_id="u1", query="ชอบ", limit=5)

    assert result["ok"] is False
    assert result["backend"] == "memory_gateway_v2_retrieve_failed"
    assert result["results"] == []


def test_list_recent_fallback_returns_ok_true():
    """list_recent_memories_v2 local fallback must return ok=True with backend=local_json_fallback_recent."""
    records = [
        _mem("u1", "ฉันชอบดาวเสาร์", 85),
        _mem("u1", "ฉันชอบดาวพฤหัส", 80),
    ]
    result = _recent_via_patch(records, user_id="u1")

    assert result["ok"] is True
    assert result["backend"] == "local_json_fallback_recent"
    assert isinstance(result["results"], list)
