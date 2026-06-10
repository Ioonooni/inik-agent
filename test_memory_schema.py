from memory_schema import (
    SCHEMA_VERSION,
    build_memory_record,
    record_to_dict,
    should_promote_to_long_term,
    merge_duplicate_memory,
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

merged = merge_duplicate_memory(d, r2)
assert merged["hit_count"] == 2
assert merged["importance"] == 80

low = build_memory_record(
    user_id="demo_user",
    content="คุยเล่นหน่อย",
    memory_type="low_value_chat",
    importance=10,
)

assert should_promote_to_long_term(low) is False

print("MEMORY SCHEMA TESTS PASSED")
