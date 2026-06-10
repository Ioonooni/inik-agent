from memory_pipeline import build_memory_from_message
from supabase_memory_v2 import make_memory_payload, TABLE_NAME


record = build_memory_from_message(
    user_id="demo_user",
    message="ฉันชอบดาวเสาร์",
)

assert record is not None

payload = make_memory_payload(record)

assert payload["memory_id"] == record["memory_id"]
assert payload["user_id"] == "demo_user"
assert payload["content"] == "ฉันชอบดาวเสาร์"
assert payload["schema_version"] == "memory_v2"
assert payload["metadata"]["promote_to_long_term"] is True
assert TABLE_NAME == "memories_v2"

try:
    make_memory_payload({"memory_id": "x"})
    raise AssertionError("missing fields should raise")
except ValueError:
    pass

print("SUPABASE MEMORY V2 TESTS PASSED")
