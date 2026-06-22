from datetime import datetime, timezone, timedelta

from memory_lifecycle import (
    compress_memory_summary,
    enforce_active_memory_limit,
    is_archive_candidate,
    mark_archive_candidates,
)


def mem(
    memory_id,
    content,
    memory_type="user_fact",
    importance=80,
    hit_count=1,
    age_days=0,
    metadata=None,
):
    ts = (datetime.now(timezone.utc) - timedelta(days=age_days)).isoformat()
    return {
        "memory_id": memory_id,
        "user_id": "u1",
        "content": content,
        "memory_type": memory_type,
        "importance": importance,
        "hit_count": hit_count,
        "created_at": ts,
        "last_seen_at": ts,
        "metadata": metadata or {},
    }


def run():
    active = mem("a", "ฉันชื่อไออุ่น", importance=95, hit_count=5)
    low = mem("b", "คุยเล่นทั่วไป", memory_type="low_value_chat", importance=20)
    old_weak = mem("c", "เรื่องเล็กมาก", importance=20, hit_count=1, age_days=400)
    superseded = mem("d", "ฉันชอบดาวพฤหัส", importance=85, metadata={"superseded": True})

    assert is_archive_candidate(active) is False
    assert is_archive_candidate(low) is True
    assert is_archive_candidate(old_weak) is True
    assert is_archive_candidate(superseded) is True

    marked = mark_archive_candidates([active, low, old_weak, superseded])
    archived = [m for m in marked if m["metadata"].get("archived") is True]

    assert len(archived) == 3
    assert active["metadata"] == {}, "must not mutate input"

    summary = compress_memory_summary(marked)

    assert summary["schema"] == "memory_lifecycle_summary_v1"
    assert summary["total_memories"] == 4
    assert summary["active_count"] == 1
    assert summary["archive_candidate_count"] == 3
    assert "ฉันชื่อไออุ่น" in summary["highlights"][0]

    many = [
        mem(f"id-{i}", f"memory {i}", importance=80 - i, hit_count=1)
        for i in range(8)
    ]
    limited = enforce_active_memory_limit(many, max_active=3)
    active_after_limit = [
        m for m in limited
        if not m["metadata"].get("archived")
    ]

    assert len(active_after_limit) == 3

    print("memory lifecycle ok")


if __name__ == "__main__":
    run()
