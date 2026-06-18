"""
Phase 4.1A — legacy RAG fallback now applies rank_memories().

Supabase modules are stubbed at import time so rag_memory is importable
without streamlit. Individual tests patch the Supabase callsites inside
rag_memory to trigger the fallback path.
"""
import sys
from unittest.mock import MagicMock, patch

# Stub unavailable Supabase deps before importing rag_memory
for _m in ("supabase_memory", "supabase_memory_v2"):
    sys.modules.setdefault(_m, MagicMock())

from rag_memory import search_memory_notes, list_recent_memory_notes  # noqa: E402  (must come after stubs)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_client(data: list) -> MagicMock:
    """Return a minimal Supabase-like mock that yields data for any table query."""
    mock_result = MagicMock()
    mock_result.data = data
    client = MagicMock()
    (
        client.table.return_value
        .select.return_value
        .eq.return_value
        .ilike.return_value
        .order.return_value
        .limit.return_value
        .execute.return_value
    ) = mock_result
    return client


def _fallback(query: str, data: list, limit: int = 5) -> dict:
    """Call search_memory_notes with search_supabase_memories forced to fail."""
    client = _make_client(data)
    with patch("rag_memory.get_supabase_client", return_value=client), \
         patch("rag_memory.search_supabase_memories",
               side_effect=Exception("supabase_v2 unavailable")):
        return search_memory_notes("u1", query, limit=limit)


def _mem(content, importance, *, superseded=False,
         ts="2026-06-10T00:00:00+00:00") -> dict:
    m = {
        "content": content,
        "memory_type": "user_fact",
        "importance": importance,
        "hit_count": 1,
        "last_seen_at": ts,
    }
    if superseded:
        m["metadata"] = {"superseded": True}
    return m


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_fallback_results_receive_rank_score():
    """Fallback results must carry rank_score after Phase 4.1A fix."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 85),
        _mem("ฉันชอบดาวพฤหัส", 80),
    ]
    result = _fallback("ชอบ", data)

    assert result["ok"] is True
    assert result["backend"] == "legacy_rag_fallback"
    assert all("rank_score" in m for m in result["results"])


def test_fallback_results_ordered_by_phase3_ranking():
    """Higher effective_importance → higher rank_score → appears first."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 40),   # lower importance — Supabase returned first
        _mem("ฉันชอบดาวพฤหัส", 85),   # higher importance
    ]
    result = _fallback("ชอบ", data)

    assert result["ok"] is True
    scores = [m["rank_score"] for m in result["results"]]
    assert scores == sorted(scores, reverse=True)
    assert result["results"][0]["importance"] == 85


def test_fallback_superseded_ranks_below_active():
    """Superseded memory (0.25× effective_importance) must land below active memory."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 85, superseded=True),   # returned first by legacy
        _mem("ฉันชอบดาวพฤหัส", 85),                    # active
    ]
    result = _fallback("ชอบ", data)

    assert result["ok"] is True
    assert len(result["results"]) == 2
    assert result["results"][0].get("metadata", {}).get("superseded") is not True
    assert result["results"][-1]["metadata"]["superseded"] is True


def _make_recent_client(data: list) -> MagicMock:
    """Return a mock for the list_recent_memory_notes legacy query chain (no ilike)."""
    mock_result = MagicMock()
    mock_result.data = data
    client = MagicMock()
    (
        client.table.return_value
        .select.return_value
        .eq.return_value
        .order.return_value
        .limit.return_value
        .execute.return_value
    ) = mock_result
    return client


def _recent_primary(data: list, limit: int = 10) -> dict:
    """Call list_recent_memory_notes with list_supabase_memories returning data."""
    with patch("rag_memory.get_supabase_client", return_value=MagicMock()), \
         patch("rag_memory.list_supabase_memories", return_value=data):
        return list_recent_memory_notes("u1", limit=limit)


def _recent_fallback(data: list, limit: int = 10) -> dict:
    """Call list_recent_memory_notes with list_supabase_memories forced to fail."""
    client = _make_recent_client(data)
    with patch("rag_memory.get_supabase_client", return_value=client), \
         patch("rag_memory.list_supabase_memories",
               side_effect=Exception("supabase_v2 unavailable")):
        return list_recent_memory_notes("u1", limit=limit)


def test_recent_primary_results_receive_rank_score():
    """list_recent primary path must attach rank_score to every result."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 85),
        _mem("ฉันชอบดาวพฤหัส", 80),
    ]
    result = _recent_primary(data)

    assert result["ok"] is True
    assert result["backend"] == "memories_v2"
    assert all("rank_score" in m for m in result["results"])


def test_recent_primary_results_ordered_by_rank_score():
    """list_recent primary path must sort results by rank_score descending."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 40),   # lower importance — returned first by mock
        _mem("ฉันชอบดาวพฤหัส", 85),   # higher importance
    ]
    result = _recent_primary(data)

    assert result["ok"] is True
    scores = [m["rank_score"] for m in result["results"]]
    assert scores == sorted(scores, reverse=True)
    assert result["results"][0]["importance"] == 85


def test_recent_legacy_fallback_results_receive_rank_score():
    """list_recent legacy fallback must attach rank_score to every result."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 85),
        _mem("ฉันชอบดาวพฤหัส", 80),
    ]
    result = _recent_fallback(data)

    assert result["ok"] is True
    assert result["backend"] == "legacy_rag_fallback"
    assert all("rank_score" in m for m in result["results"])


def test_recent_legacy_fallback_results_ordered_by_rank_score():
    """list_recent legacy fallback must sort results by rank_score descending."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 40),   # lower importance — returned first by mock
        _mem("ฉันชอบดาวพฤหัส", 85),   # higher importance
    ]
    result = _recent_fallback(data)

    assert result["ok"] is True
    scores = [m["rank_score"] for m in result["results"]]
    assert scores == sorted(scores, reverse=True)
    assert result["results"][0]["importance"] == 85


def test_recent_superseded_ranks_below_active():
    """Superseded recent memory must rank below active recent memory (both paths)."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 85, superseded=True),   # returned first by mock
        _mem("ฉันชอบดาวพฤหัส", 85),                    # active
    ]
    for result in (_recent_primary(data), _recent_fallback(data)):
        assert result["ok"] is True
        assert len(result["results"]) == 2
        assert result["results"][0].get("metadata", {}).get("superseded") is not True
        assert result["results"][-1]["metadata"]["superseded"] is True


def test_fallback_limit_is_respected():
    """rank_memories limit parameter must cap returned results."""
    data = [
        _mem("ฉันชอบดาวเสาร์", 80),
        _mem("ฉันชอบดาวพฤหัส", 85),
        _mem("ฉันชอบดาวอังคาร", 70),
    ]
    result = _fallback("ชอบ", data, limit=2)

    assert result["ok"] is True
    assert len(result["results"]) <= 2
