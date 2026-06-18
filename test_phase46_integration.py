"""
Phase 4.6 — End-to-end integration verification for the complete Memory V2 runtime path.

Tests the full chain:
  save_message_memory_v2 → conflict detection → soft supersede
  → retrieval → rank_memories → local fallback → list_recent_memory_notes

All Supabase I/O is mocked. memory_quality, memory_schema, memory_pipeline,
memory_ranking, and memory_store_v2 execute their real logic.
"""
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

# Stub Supabase modules before importing any gateway or RAG code
for _m in ("supabase_memory", "supabase_memory_v2"):
    sys.modules.setdefault(_m, MagicMock())

import rag_memory  # noqa: E402 — must come after stubs; ensures module is in sys.modules for patching
from memory_gateway_v2 import (  # noqa: E402
    save_message_memory_v2,
    retrieve_memories_v2,
    list_recent_memories_v2,
)
from memory_ranking import rank_memories  # noqa: E402
from memory_store_v2 import upsert_memory_record, list_memories  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_RECENT_TS = "2026-06-17T12:00:00+00:00"


def _mem(content, importance, *, superseded=False, hit_count=1,
         ts=_RECENT_TS, user_id="u1", memory_id=None) -> dict:
    m = {
        "memory_id": memory_id or str(abs(hash(content)))[:10],
        "user_id": user_id,
        "content": content,
        "memory_type": "user_fact",
        "importance": importance,
        "hit_count": hit_count,
        "last_seen_at": ts,
        "created_at": ts,
        "metadata": {},
    }
    if superseded:
        m["metadata"] = {"superseded": True}
    return m


def _tmp_store() -> str:
    """Return path to a fresh (non-existent) temp JSON store; caller must clean up."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)  # let memory_store_v2 create it fresh on first write
    return path


# ---------------------------------------------------------------------------
# Test 1: Duplicate memory reinforcement survives retrieval
# ---------------------------------------------------------------------------

def test_duplicate_reinforcement_survives_retrieval():
    """Two saves of identical content → hit_count=2 + importance reinforcement; rank_score reflects both."""
    tmp = _tmp_store()
    try:
        upsert_memory_record(_mem("ฉันชอบดาวเสาร์", 85), path=tmp)
        upsert_memory_record(_mem("ฉันชอบดาวเสาร์", 85), path=tmp)

        stored = list_memories(user_id="u1", path=tmp)
        assert len(stored) == 1
        assert stored[0]["hit_count"] == 2
        # reinforcement_bonus = min(20, (2-1)*2) = 2; 85+2 = 87
        assert stored[0]["importance"] == 87

        ranked = rank_memories(stored, limit=5, query="")
        assert "rank_score" in ranked[0]
        # hit_count*0.5 = 1.0 is part of rank_score; score must be positive
        assert ranked[0]["rank_score"] > 0
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# Test 2: Conflicting preference causes old memory to rank lower
# ---------------------------------------------------------------------------

def test_conflicting_preference_ranks_lower():
    """Superseded memory (0.25× effective_importance) ranks below its active replacement."""
    active = _mem("ฉันชอบดาวเสาร์", 85)
    old = _mem("ฉันชอบดาวพฤหัส", 85, superseded=True)

    ranked = rank_memories([old, active], limit=5, query="ชอบ")

    assert len(ranked) == 2
    assert ranked[0]["content"] == "ฉันชอบดาวเสาร์"
    assert ranked[-1]["metadata"].get("superseded") is True
    assert ranked[0]["rank_score"] > ranked[-1]["rank_score"]


# ---------------------------------------------------------------------------
# Test 3: Superseded memory remains stored but loses ranking
# ---------------------------------------------------------------------------

def test_superseded_memory_stored_but_ranked_last():
    """Superseded memory is never deleted from the store; it ranks below every active memory."""
    tmp = _tmp_store()
    try:
        active = _mem("ฉันชอบดาวเสาร์", 85, memory_id="active01")
        superseded = _mem("ฉันชอบดาวพฤหัส", 85, superseded=True, memory_id="super01")

        upsert_memory_record(active, path=tmp)
        upsert_memory_record(superseded, path=tmp)

        stored = list_memories(user_id="u1", path=tmp)
        assert len(stored) == 2, "superseded record must not be deleted"

        ranked = rank_memories(stored, limit=5, query="ชอบ")
        assert any(m["metadata"].get("superseded") is True for m in ranked)
        assert ranked[-1]["metadata"].get("superseded") is True
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# Test 4: Retrieval returns ranked results (primary V2 path)
# ---------------------------------------------------------------------------

def test_retrieval_primary_returns_ranked():
    """retrieve_memories_v2 via V2 backend returns rank_score on every result, sorted descending."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 40),   # lower importance — mock returns this first
        _mem("ฉันชอบดาวพฤหัส", 85),   # higher importance
    ]

    with patch("rag_memory.get_supabase_client", return_value=MagicMock()), \
         patch("rag_memory.search_supabase_memories", return_value=data), \
         patch("rag_memory.mark_supabase_memories_used", return_value={}):
        result = retrieve_memories_v2("u1", "ชอบ")

    assert result["ok"] is True
    assert all("rank_score" in m for m in result["results"])
    scores = [m["rank_score"] for m in result["results"]]
    assert scores == sorted(scores, reverse=True)
    assert result["results"][0]["importance"] == 85


# ---------------------------------------------------------------------------
# Test 5: list_recent returns ranked results
# ---------------------------------------------------------------------------

def test_list_recent_returns_ranked():
    """list_recent_memories_v2 returns rank_score on every result, sorted descending."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 40),
        _mem("ฉันชอบดาวพฤหัส", 85),
    ]

    with patch("rag_memory.get_supabase_client", return_value=MagicMock()), \
         patch("rag_memory.list_supabase_memories", return_value=data):
        result = list_recent_memories_v2("u1")

    assert result["ok"] is True
    assert all("rank_score" in m for m in result["results"])
    scores = [m["rank_score"] for m in result["results"]]
    assert scores == sorted(scores, reverse=True)
    assert result["results"][0]["importance"] == 85


# ---------------------------------------------------------------------------
# Test 6: Local fallback returns ranked results
# ---------------------------------------------------------------------------

def test_local_fallback_returns_ranked():
    """When search_memory_notes raises, retrieve_memories_v2 falls back to local JSON + rank_memories."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 40),
        _mem("ฉันชอบดาวพฤหัส", 85),
    ]

    with patch("rag_memory.search_memory_notes", side_effect=Exception("rag unavailable")), \
         patch("memory_gateway_v2.list_memories", return_value=data):
        result = retrieve_memories_v2("u1", "ชอบ")

    assert result["ok"] is True
    assert result["backend"] == "local_json_fallback"
    assert all("rank_score" in m for m in result["results"])
    scores = [m["rank_score"] for m in result["results"]]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# Test 7: Write path failure falls back safely
# ---------------------------------------------------------------------------

def test_write_path_failure_falls_back_safely():
    """Supabase write failure → local_fallback; ok=True, record preserved in local store."""
    tmp = _tmp_store()
    try:
        with patch("memory_gateway_v2.get_supabase_client", return_value=MagicMock()), \
             patch("memory_gateway_v2.fetch_conflictable_memories", return_value=[]), \
             patch("memory_gateway_v2.upsert_supabase_memory",
                   side_effect=Exception("connection timeout")), \
             patch("memory_gateway_v2.upsert_memory_record",
                   side_effect=lambda r: upsert_memory_record(r, path=tmp)):
            result = save_message_memory_v2("u1", "ฉันชอบดาวเสาร์")

        assert result["ok"] is True
        assert result["stored"] is True
        assert result["backend"] == "local_fallback"
        assert "supabase_error" in result
        assert result["conflict_summary"]["reason"] == "supabase_unavailable_local_fallback"

        stored = list_memories(user_id="u1", path=tmp)
        assert len(stored) == 1
        assert stored[0]["content"] == "ฉันชอบดาวเสาร์"
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# Test 8: End-to-end name memory save and recall
# ---------------------------------------------------------------------------

def test_e2e_name_save_and_recall():
    """Save a name fact through save_message_memory_v2 then recall it via retrieve_memories_v2."""
    captured = []

    def capture_upsert(client, record):
        captured.append(record)
        return {"ok": True}

    with patch("memory_gateway_v2.get_supabase_client", return_value=MagicMock()), \
         patch("memory_gateway_v2.fetch_conflictable_memories", return_value=[]), \
         patch("memory_gateway_v2.upsert_supabase_memory", side_effect=capture_upsert), \
         patch("memory_gateway_v2.supersede_supabase_memory", return_value={"ok": True}):
        save_result = save_message_memory_v2("u1", "ฉันชื่อนิค")

    assert save_result["ok"] is True
    assert save_result["stored"] is True
    assert len(captured) == 1
    saved = captured[0]
    assert saved["content"] == "ฉันชื่อนิค"
    assert saved["memory_type"] == "user_fact"
    assert saved["importance"] == 95  # name prefix → importance 95

    # Recall via V2 search path
    with patch("rag_memory.get_supabase_client", return_value=MagicMock()), \
         patch("rag_memory.search_supabase_memories", return_value=[saved]), \
         patch("rag_memory.mark_supabase_memories_used", return_value={}):
        recall = retrieve_memories_v2("u1", "ชื่อ")

    assert recall["ok"] is True
    assert len(recall["results"]) >= 1
    assert recall["results"][0]["content"] == "ฉันชื่อนิค"
    assert "rank_score" in recall["results"][0]


# ---------------------------------------------------------------------------
# Test 9: End-to-end preference update then retrieval prefers newest
# ---------------------------------------------------------------------------

def test_e2e_preference_update_prefers_newest():
    """New preference supersedes old via conflict detection → old ranks below new after retrieval."""
    old_ts = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()

    old_memory = {
        "memory_id": "old_pref_abc123",
        "user_id": "u1",
        "content": "ฉันชอบดาวพฤหัส",
        "memory_type": "user_fact",
        "importance": 85,
        "hit_count": 1,
        "last_seen_at": old_ts,
        "created_at": old_ts,
        "metadata": {},
    }

    superseded_ids = []

    def mock_supersede(client, memory_id, metadata):
        superseded_ids.append(memory_id)
        return {"ok": True}

    with patch("memory_gateway_v2.get_supabase_client", return_value=MagicMock()), \
         patch("memory_gateway_v2.fetch_conflictable_memories", return_value=[old_memory]), \
         patch("memory_gateway_v2.upsert_supabase_memory", return_value={"ok": True}), \
         patch("memory_gateway_v2.supersede_supabase_memory", side_effect=mock_supersede):
        result = save_message_memory_v2("u1", "ฉันชอบดาวเสาร์")

    assert result["ok"] is True
    assert result["conflict_summary"]["superseded"] == 1
    assert "old_pref_abc123" in superseded_ids

    # Build the post-save state seen by the retrieval layer
    new_record = result["record"]
    superseded_old = dict(old_memory, metadata={"superseded": True})

    ranked = rank_memories([superseded_old, new_record], limit=5, query="ชอบ")

    assert ranked[0]["content"] == "ฉันชอบดาวเสาร์"
    assert ranked[-1]["metadata"].get("superseded") is True
    assert ranked[0]["rank_score"] > ranked[-1]["rank_score"]


# ---------------------------------------------------------------------------
# Test 10: No production code mutation during ranking
# ---------------------------------------------------------------------------

def test_no_production_code_mutation_during_ranking():
    """rank_memories creates new dicts with rank_score; stored importance and metadata are unchanged."""
    original = _mem("ฉันชอบดาวเสาร์", 85)
    original_importance = original["importance"]
    original_metadata = dict(original.get("metadata") or {})

    ranked = rank_memories([original], limit=5, query="ชอบ")

    assert "rank_score" in ranked[0]          # copy carries rank_score
    assert "rank_score" not in original       # original is not mutated
    assert original["importance"] == original_importance
    assert original.get("metadata") == original_metadata
