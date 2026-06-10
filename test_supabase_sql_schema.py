from pathlib import Path

sql = Path("supabase/memories_v2.sql").read_text(encoding="utf-8").lower()

required = [
    "create table if not exists public.memories_v2",
    "memory_id text primary key",
    "user_id text not null",
    "content text not null",
    "importance integer",
    "metadata jsonb",
    "enable row level security",
    "idx_memories_v2_user_id",
    "idx_memories_v2_user_importance",
    "idx_memories_v2_user_last_seen",
]

for item in required:
    assert item in sql, item

print("SUPABASE SQL SCHEMA TESTS PASSED")
