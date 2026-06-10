from pathlib import Path

from memory_pipeline import build_memory_from_message
from memory_store_v2 import (
    list_memories,
    reset_memory_store,
    search_memories,
    upsert_memory_record,
)

TEST_PATH = "tmp_memory_store_v2_test.json"

reset_memory_store(TEST_PATH)

record = build_memory_from_message("demo_user", "ฉันชอบดาวเสาร์")
assert record is not None

result = upsert_memory_record(record, TEST_PATH)
assert result["ok"] is True
assert result["action"] == "inserted"

memories = list_memories("demo_user", TEST_PATH)
assert len(memories) == 1
assert memories[0]["content"] == "ฉันชอบดาวเสาร์"

result2 = upsert_memory_record(record, TEST_PATH)
assert result2["action"] == "merged"
assert result2["record"]["hit_count"] == 2

found = search_memories("ดาวเสาร์", "demo_user", TEST_PATH)
assert len(found) == 1
assert found[0]["content"] == "ฉันชอบดาวเสาร์"

none = search_memories("หลุมดำ", "demo_user", TEST_PATH)
assert none == []

Path(TEST_PATH).unlink(missing_ok=True)

print("MEMORY STORE V2 TESTS PASSED")
