"""
Phase 3 Memory Intelligence — end-to-end recall verification tests.
All tests use a local temp JSON store; no Supabase dependency.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from memory_pipeline import build_memory_from_message
from memory_ranking import effective_importance, rank_memories
from memory_schema import detect_memory_conflict, mark_memory_superseded
from memory_store_v2 import (
    list_memories,
    reset_memory_store,
    search_memories,
    upsert_memory_record,
)

_STORE = "tmp_phase3_intelligence_test.json"


@pytest.fixture(autouse=True)
def clean_store():
    reset_memory_store(_STORE)
    yield
    Path(_STORE).unlink(missing_ok=True)


# ── 1. Importance + Store + Search ──────────────────────────────────────────

def test_name_memory_stored_with_high_importance_and_searchable():
    """Phase 3.1: name facts get importance=95 and are retrievable by search."""
    record = build_memory_from_message("u1", "ฉันชื่อไออุ่น")
    assert record is not None
    assert record["importance"] >= 90  # name = 95

    upsert_memory_record(record, _STORE)

    results = search_memories("ไออุ่น", user_id="u1", path=_STORE)
    assert len(results) == 1
    assert results[0]["content"] == "ฉันชื่อไออุ่น"


# ── 2. Reinforcement ─────────────────────────────────────────────────────────

def test_reinforcement_hit_count_and_importance_increase():
    """Phase 3.2: upserting the same memory twice increments hit_count and boosts importance."""
    record = build_memory_from_message("u1", "ฉันชื่อไออุ่น")
    assert record is not None

    r1 = upsert_memory_record(record, _STORE)
    assert r1["action"] == "inserted"
    base_importance = r1["record"]["importance"]

    r2 = upsert_memory_record(record, _STORE)
    assert r2["action"] == "merged"
    assert r2["record"]["hit_count"] == 2
    # bonus = min(20, (2-1)*2) = 2 => importance rises by 2
    assert r2["record"]["importance"] > base_importance


# ── 3. Decay ranking ─────────────────────────────────────────────────────────

def test_decay_old_user_fact_outranks_old_conversation_event():
    """Phase 3.3: at the same age, user_fact decays much slower than conversation_event."""
    def _aged(content, memory_type, importance, age_days):
        ts = (datetime.now(timezone.utc) - timedelta(days=age_days)).isoformat()
        return {
            "content": content,
            "memory_type": memory_type,
            "importance": importance,
            "hit_count": 1,
            "last_seen_at": ts,
        }

    old_fact = _aged("ฉันชื่อไออุ่น", "user_fact", 80, age_days=180)
    old_event = _aged("คุยกันเรื่องดาว", "conversation_event", 80, age_days=180)

    # user_fact:         rate=0.02, 6 periods → 80 * 0.88 = 70.4
    # conversation_event: rate=0.15, 6 periods → 80 * max(0.30, 0.10) = 24.0
    assert effective_importance(old_fact) > effective_importance(old_event)


# ── 4. Conflict detection ────────────────────────────────────────────────────

def test_conflict_detection_preference_category():
    """Phase 3.4A: two different preferences for the same user are flagged as a conflict."""
    existing = {
        "user_id": "u1",
        "content": "ฉันชอบดาวเสาร์",
        "memory_type": "user_fact",
        "last_seen_at": "2026-01-01T00:00:00+00:00",
    }
    incoming = {
        "user_id": "u1",
        "content": "ฉันชอบดาวพฤหัส",
        "memory_type": "user_fact",
        "last_seen_at": "2026-06-01T00:00:00+00:00",
    }

    result = detect_memory_conflict(existing, incoming)
    assert result["conflict"] is True
    assert result["category"] == "preference"
    assert result["winner"] == "incoming"


# ── 5. Soft supersede ────────────────────────────────────────────────────────

def test_soft_supersede_marks_old_and_new_ranks_higher():
    """Phase 3.4B: older preference gets superseded metadata; newer preference ranks above it."""
    old = {
        "user_id": "u1",
        "content": "ฉันชอบดาวเสาร์",
        "memory_type": "user_fact",
        "importance": 85,
        "hit_count": 1,
        "memory_id": "old_pref_001",
        "last_seen_at": "2026-01-01T00:00:00+00:00",
    }
    new = {
        "user_id": "u1",
        "content": "ฉันชอบดาวพฤหัส",
        "memory_type": "user_fact",
        "importance": 85,
        "hit_count": 1,
        "memory_id": "new_pref_002",
        "last_seen_at": "2026-06-01T00:00:00+00:00",
    }

    superseded_old = mark_memory_superseded(old, new)
    assert superseded_old["metadata"]["superseded"] is True
    assert superseded_old["metadata"]["superseded_by"] == "new_pref_002"

    ranked = rank_memories([superseded_old, new])
    assert ranked[0]["memory_id"] == "new_pref_002"
    assert ranked[-1]["metadata"].get("superseded") is True


# ── 6. Store keeps both records; superseded one ranks lower ──────────────────

def test_store_keeps_both_records_and_superseded_ranks_lower():
    """Phase 3.4B + store: both old and new records persist; soft supersede only affects rank."""
    old_pref = build_memory_from_message("u1", "ฉันชอบดาวเสาร์")
    new_pref = build_memory_from_message("u1", "ฉันชอบดาวพฤหัส")
    assert old_pref is not None
    assert new_pref is not None

    upsert_memory_record(old_pref, _STORE)
    upsert_memory_record(new_pref, _STORE)

    # Both records must remain in store — no deletion on conflict
    assert len(list_memories("u1", _STORE)) == 2

    # Simulate old < new by assigning explicit timestamps for winner resolution
    old_pref["last_seen_at"] = "2026-01-01T00:00:00+00:00"
    new_pref["last_seen_at"] = "2026-06-01T00:00:00+00:00"

    superseded = mark_memory_superseded(old_pref, new_pref)

    ranked = rank_memories([superseded, new_pref])
    assert ranked[0]["content"] == new_pref["content"]
    assert ranked[1]["metadata"]["superseded"] is True
