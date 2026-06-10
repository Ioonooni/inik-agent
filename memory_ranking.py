from datetime import datetime, timezone


def memory_score(memory: dict) -> float:
    score = 0.0

    score += float(memory.get("importance", 0))

    score += float(memory.get("hit_count", 0)) * 0.5

    try:
        ts = memory.get("last_seen_at")

        if ts:
            dt = datetime.fromisoformat(
                ts.replace("Z", "+00:00")
            )

            age_days = (
                datetime.now(timezone.utc) - dt
            ).days

            score += max(
                0,
                30 - age_days
            ) * 0.2

    except Exception:
        pass

    return round(score, 2)


def rank_memories(memories, limit=5):
    ranked = sorted(
        memories,
        key=memory_score,
        reverse=True
    )

    return ranked[:limit]
