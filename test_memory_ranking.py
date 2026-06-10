from memory_ranking import rank_memories

memories = [
    {
        "content":"A",
        "importance":10,
        "hit_count":1,
        "last_seen_at":"2026-06-01T00:00:00+00:00"
    },
    {
        "content":"B",
        "importance":80,
        "hit_count":3,
        "last_seen_at":"2026-06-10T00:00:00+00:00"
    },
    {
        "content":"C",
        "importance":20,
        "hit_count":1,
        "last_seen_at":"2026-06-09T00:00:00+00:00"
    }
]

ranked = rank_memories(memories)

assert ranked[0]["content"] == "B"

print("MEMORY RANKING TESTS PASSED")
