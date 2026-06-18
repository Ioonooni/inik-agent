from datetime import datetime, timezone
from typing import Iterable


_DECAY_RATES: dict[str, float] = {
    "user_fact": 0.02,
    "preference": 0.02,
    "emotional_event": 0.08,
    "conversation_event": 0.15,
    "low_value_chat": 0.20,
}
_DEFAULT_DECAY_RATE = 0.20


def _normalize_text(value: object) -> str:
    return str(value or "").strip().lower()


def _query_terms(query: str) -> list[str]:
    return [
        term
        for term in _normalize_text(query).replace(",", " ").split()
        if len(term) >= 2
    ]


def _age_days(memory: dict) -> float:
    try:
        ts = memory.get("last_seen_at") or memory.get("created_at")
        if not ts:
            return 0.0
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return float((datetime.now(timezone.utc) - dt).days)
    except Exception:
        return 0.0


def relevance_score(memory: dict, query: str = "") -> float:
    content = _normalize_text(memory.get("content"))
    memory_type = _normalize_text(memory.get("memory_type"))
    terms = _query_terms(query)

    if not terms:
        return 0.0

    score = 0.0

    for term in terms:
        if term in content:
            score += 8.0
        if term in memory_type:
            score += 2.0

    if _normalize_text(query) and _normalize_text(query) in content:
        score += 12.0

    return score


def recency_score(memory: dict) -> float:
    try:
        ts = memory.get("last_seen_at") or memory.get("created_at")

        if not ts:
            return 0.0

        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))

        age_days = (datetime.now(timezone.utc) - dt).days

        return max(0.0, 30.0 - float(age_days)) * 0.2

    except Exception:
        return 0.0


def importance_score(memory: dict) -> float:
    metadata = memory.get("metadata") or {}

    try:
        return float(memory.get("importance", metadata.get("importance", 0)))
    except (TypeError, ValueError):
        return 0.0


def effective_importance(memory: dict) -> float:
    """Return decayed importance for ranking — does not touch stored importance."""
    base = importance_score(memory)

    memory_type = _normalize_text(memory.get("memory_type"))
    decay_rate = _DECAY_RATES.get(memory_type, _DEFAULT_DECAY_RATE)

    hit_count = int(memory.get("hit_count", 1))
    if hit_count >= 10:
        decay_rate *= 0.25
    elif hit_count >= 5:
        decay_rate *= 0.5

    decay_periods = _age_days(memory) / 30.0
    multiplier = max(0.30, 1.0 - decay_rate * decay_periods)

    return round(base * multiplier, 2)


def memory_score(memory: dict, query: str = "") -> float:
    score = 0.0

    score += relevance_score(memory, query=query)
    score += effective_importance(memory)
    score += float(memory.get("hit_count", 0)) * 0.5
    score += recency_score(memory)

    return round(score, 2)


def rank_memories(memories: Iterable[dict], limit: int = 5, query: str = "") -> list[dict]:
    ranked = []

    for memory in memories:
        item = dict(memory)
        item["rank_score"] = memory_score(item, query=query)
        ranked.append(item)

    ranked.sort(
        key=lambda item: item.get("rank_score", 0),
        reverse=True
    )

    return ranked[:limit]
