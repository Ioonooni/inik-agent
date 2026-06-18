from datetime import datetime, timezone, timedelta

from memory_ranking import effective_importance, rank_memories


def _mem(content, importance, memory_type="user_fact", age_days=0, hit_count=1):
    ts = (datetime.now(timezone.utc) - timedelta(days=age_days)).isoformat()
    return {
        "content": content,
        "importance": importance,
        "memory_type": memory_type,
        "hit_count": hit_count,
        "last_seen_at": ts,
    }


# Existing module-level regression test (preserved)
memories = [
    {
        "content": "A",
        "importance": 10,
        "hit_count": 1,
        "last_seen_at": "2026-06-01T00:00:00+00:00",
    },
    {
        "content": "B",
        "importance": 80,
        "hit_count": 3,
        "last_seen_at": "2026-06-10T00:00:00+00:00",
    },
    {
        "content": "C",
        "importance": 20,
        "hit_count": 1,
        "last_seen_at": "2026-06-09T00:00:00+00:00",
    },
]

ranked = rank_memories(memories)

assert ranked[0]["content"] == "B"

print("MEMORY RANKING TESTS PASSED")


def test_recent_high_importance_ranks_high():
    recent = _mem("recent fact", 90, "user_fact", age_days=1)
    old_event = _mem("old chat", 40, "conversation_event", age_days=200)
    result = rank_memories([old_event, recent])
    assert result[0]["content"] == "recent fact"


def test_old_conversation_event_decays_more_than_user_fact():
    # Same importance and age — conversation_event should have lower effective importance
    fact = _mem("personal fact", 80, "user_fact", age_days=180)
    event = _mem("old conversation", 80, "conversation_event", age_days=180)
    # user_fact: rate=0.02, periods=6 => multiplier=max(0.30, 1-0.12)=0.88 => 70.4
    # conversation_event: rate=0.15, periods=6 => multiplier=max(0.30, 1-0.90)=0.30 => 24.0
    assert effective_importance(fact) > effective_importance(event)


def test_high_hit_count_slows_decay():
    # emotional_event at 90 days: hit_count=1 vs hit_count=10
    low_hits = _mem("memory", 60, "emotional_event", age_days=90, hit_count=1)
    high_hits = _mem("memory", 60, "emotional_event", age_days=90, hit_count=10)
    # low:  rate=0.08, periods=3 => multiplier=max(0.30,1-0.24)=0.76 => 45.6
    # high: rate=0.08*0.25=0.02, periods=3 => multiplier=max(0.30,1-0.06)=0.94 => 56.4
    assert effective_importance(high_hits) > effective_importance(low_hits)


def test_stored_importance_not_modified():
    mem = _mem("my cat", 85, "user_fact", age_days=30)
    original = mem["importance"]
    rank_memories([mem])
    assert mem["importance"] == original


def test_rank_memories_returns_rank_score():
    mems = [_mem("a", 50, "user_fact", age_days=5), _mem("b", 30, "user_fact", age_days=5)]
    result = rank_memories(mems)
    assert all("rank_score" in m for m in result)


# ---------------------------------------------------------------------------
# Phase 3.4B — supersede penalty tests
# ---------------------------------------------------------------------------

def _superseded_mem(content, importance, memory_type="user_fact", age_days=0, hit_count=1):
    m = _mem(content, importance, memory_type, age_days, hit_count)
    m["metadata"] = {"superseded": True}
    return m


def test_superseded_memory_has_lower_effective_importance():
    normal = _mem("ฉันชื่อไออุ่น", 90, "user_fact", age_days=0)
    superseded = _superseded_mem("ฉันชื่อไออุ่น", 90, "user_fact", age_days=0)
    assert effective_importance(superseded) < effective_importance(normal)


def test_rank_places_non_superseded_above_superseded():
    superseded = _superseded_mem("ฉันชื่อไออุ่น", 90, "user_fact", age_days=0)
    active = _mem("ฉันชื่ออุ่น", 90, "user_fact", age_days=0)
    result = rank_memories([superseded, active])
    assert result[0]["content"] == "ฉันชื่ออุ่น"


def test_rank_does_not_mutate_stored_superseded_input():
    mem = _superseded_mem("ฉันชื่อไออุ่น", 90, "user_fact", age_days=0)
    original_importance = mem["importance"]
    rank_memories([mem])
    assert mem["importance"] == original_importance
    assert mem["metadata"]["superseded"] is True
