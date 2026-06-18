from memory_schema import (
    SCHEMA_VERSION,
    build_memory_record,
    record_to_dict,
    should_promote_to_long_term,
    merge_duplicate_memory,
    detect_memory_conflict,
)

r = build_memory_record(
    user_id="demo_user",
    content="ฉันชอบดาวเสาร์",
    memory_type="preference",
    importance=80,
)

assert r.schema_version == SCHEMA_VERSION
assert r.user_id == "demo_user"
assert r.content == "ฉันชอบดาวเสาร์"
assert r.importance == 80
assert r.hit_count == 1
assert should_promote_to_long_term(r) is True

d = record_to_dict(r)
assert d["memory_id"] == r.memory_id

r2 = build_memory_record(
    user_id="demo_user",
    content="ฉันชอบดาวเสาร์",
    memory_type="preference",
    importance=40,
)

assert r.memory_id == r2.memory_id

# hit_count 2: base=max(80,40)=80, bonus=min(20,(2-1)*2)=2, importance=82
merged = merge_duplicate_memory(d, r2)
assert merged["hit_count"] == 2
assert merged["importance"] == 82
assert merged["metadata"]["reinforced"] is True
assert merged["metadata"]["reinforcement_bonus"] == 2

low = build_memory_record(
    user_id="demo_user",
    content="คุยเล่นหน่อย",
    memory_type="low_value_chat",
    importance=10,
)

assert should_promote_to_long_term(low) is False

print("MEMORY SCHEMA TESTS PASSED")


def test_merge_increases_hit_count():
    base = record_to_dict(build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 80))
    incoming = build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 40)
    result = merge_duplicate_memory(base, incoming)
    assert result["hit_count"] == 2


def test_merge_importance_82_on_second_hit():
    base = record_to_dict(build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 80))
    incoming = build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 40)
    result = merge_duplicate_memory(base, incoming)
    # hit_count=2, base=80, bonus=min(20,(2-1)*2)=2 => 82
    assert result["importance"] == 82


def test_merge_importance_88_on_fifth_hit():
    base = record_to_dict(build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 80))
    base["hit_count"] = 4  # simulate 4 prior hits
    incoming = build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 40)
    result = merge_duplicate_memory(base, incoming)
    # hit_count=5, base=80, bonus=min(20,(5-1)*2)=8 => 88
    assert result["hit_count"] == 5
    assert result["importance"] == 88


def test_merge_importance_caps_at_100():
    base = record_to_dict(build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 95))
    base["hit_count"] = 50
    incoming = build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 95)
    result = merge_duplicate_memory(base, incoming)
    # hit_count=51, base=95, bonus=min(20,50*2)=20 => min(100,115)=100
    assert result["importance"] == 100


def test_merge_preserves_and_adds_metadata():
    base = record_to_dict(build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 80,
                                               metadata={"promote_to_long_term": True}))
    incoming = build_memory_record("u", "ฉันชื่อไออุ่น", "user_fact", 40)
    result = merge_duplicate_memory(base, incoming)
    assert result["metadata"]["promote_to_long_term"] is True  # preserved
    assert result["metadata"]["reinforced"] is True
    assert result["metadata"]["reinforcement_bonus"] == 2


# ---------------------------------------------------------------------------
# Phase 3.4A — conflict detection tests
# ---------------------------------------------------------------------------

def _fact(content, memory_type="user_fact", user_id="u", last_seen_at=None):
    return {"user_id": user_id, "content": content,
            "memory_type": memory_type, "last_seen_at": last_seen_at}


def test_conflict_name():
    r = detect_memory_conflict(
        _fact("ฉันชื่อไออุ่น"),
        _fact("ฉันชื่ออุ่น"),
    )
    assert r["conflict"] is True
    assert r["category"] == "name"


def test_conflict_preference():
    r = detect_memory_conflict(
        _fact("ฉันชอบดาวเสาร์"),
        _fact("ฉันชอบดาวพฤหัส"),
    )
    assert r["conflict"] is True
    assert r["category"] == "preference"


def test_conflict_dislike():
    r = detect_memory_conflict(
        _fact("ฉันไม่ชอบเสียงดัง"),
        _fact("ฉันไม่ชอบคนโกหก"),
    )
    assert r["conflict"] is True
    assert r["category"] == "dislike"


def test_no_conflict_different_category():
    r = detect_memory_conflict(
        _fact("ฉันชอบดาวเสาร์"),
        _fact("ฉันไม่ชอบเสียงดัง"),
    )
    assert r["conflict"] is False


def test_no_conflict_identical_content():
    r = detect_memory_conflict(
        _fact("ฉันชื่อไออุ่น"),
        _fact("ฉันชื่อไออุ่น"),
    )
    assert r["conflict"] is False


def test_no_conflict_non_user_fact():
    r = detect_memory_conflict(
        _fact("เหนื่อยมากวันนี้", memory_type="emotional_event"),
        _fact("เหนื่อยมากวันนี้", memory_type="emotional_event"),
    )
    assert r["conflict"] is False


def test_winner_newer_incoming():
    r = detect_memory_conflict(
        _fact("ฉันชื่อไออุ่น", last_seen_at="2026-01-01T00:00:00+00:00"),
        _fact("ฉันชื่ออุ่น",   last_seen_at="2026-06-01T00:00:00+00:00"),
    )
    assert r["conflict"] is True
    assert r["winner"] == "incoming"


def test_winner_newer_existing():
    r = detect_memory_conflict(
        _fact("ฉันชื่อไออุ่น", last_seen_at="2026-06-01T00:00:00+00:00"),
        _fact("ฉันชื่ออุ่น",   last_seen_at="2026-01-01T00:00:00+00:00"),
    )
    assert r["conflict"] is True
    assert r["winner"] == "existing"


def test_winner_unknown_on_missing_timestamps():
    r = detect_memory_conflict(
        _fact("ฉันชื่อไออุ่น"),
        _fact("ฉันชื่ออุ่น"),
    )
    assert r["conflict"] is True
    assert r["winner"] == "unknown"
