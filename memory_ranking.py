from datetime import datetime, timezone
from typing import Iterable


def _normalize_text(value: object) -> str:
    return str(value or "").strip().lower()


def _query_terms(query: str) -> list[str]:
    return [
        term
        for term in _normalize_text(query).replace(",", " ").split()
        if len(term) >= 2
    ]


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


def memory_score(memory: dict, query: str = "") -> float:
    score = 0.0

    score += relevance_score(memory, query=query)
    score += importance_score(memory)
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
