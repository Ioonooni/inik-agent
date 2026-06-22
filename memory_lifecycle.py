from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from memory_ranking import effective_importance, memory_score


ARCHIVE_EFFECTIVE_IMPORTANCE_THRESHOLD = 25.0
ARCHIVE_HARD_LIMIT = 50


def _memory_text(memory: Dict[str, Any]) -> str:
    for key in ("content", "text", "message", "summary"):
        value = memory.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _metadata(memory: Dict[str, Any]) -> Dict[str, Any]:
    metadata = memory.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def is_archive_candidate(memory: Dict[str, Any]) -> bool:
    """
    Decide whether a memory can be archived from active recall.

    This does not delete memory.
    It marks low-value / superseded / low-importance records as archive candidates.
    """
    metadata = _metadata(memory)

    if metadata.get("archived") is True:
        return True

    if metadata.get("superseded") is True:
        return True

    memory_type = str(memory.get("memory_type") or "").strip().lower()
    hit_count = int(memory.get("hit_count", 0) or 0)
    importance = int(memory.get("importance", 0) or 0)
    effective = effective_importance(memory)

    if memory_type == "low_value_chat":
        return True

    if effective < ARCHIVE_EFFECTIVE_IMPORTANCE_THRESHOLD and hit_count <= 1:
        return True

    if importance < 40 and hit_count <= 2:
        return True

    return False


def compress_memory_summary(memories: Iterable[Dict[str, Any]], limit: int = 12) -> Dict[str, Any]:
    """
    Build a compact lifecycle summary without vector search.

    The summary is deterministic and safe for tests:
    - counts by memory_type
    - active memory count
    - archive candidate count
    - top active memory snippets
    """
    items = [dict(memory) for memory in memories]
    type_counts = Counter(str(m.get("memory_type") or "memory") for m in items)

    active = [m for m in items if not is_archive_candidate(m)]
    archive_candidates = [m for m in items if is_archive_candidate(m)]

    active.sort(key=lambda m: memory_score(m, query=""), reverse=True)

    highlights: List[str] = []
    for memory in active[:limit]:
        text = _memory_text(memory)
        if text:
            highlights.append(text[:160])

    return {
        "schema": "memory_lifecycle_summary_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_memories": len(items),
        "active_count": len(active),
        "archive_candidate_count": len(archive_candidates),
        "memory_type_counts": dict(type_counts),
        "highlights": highlights,
    }


def mark_archive_candidates(memories: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Return copied records with metadata.archived=True for archive candidates.

    This is non-destructive:
    - does not mutate input
    - does not delete records
    - does not require schema migration
    """
    result: List[Dict[str, Any]] = []

    for memory in memories:
        item = dict(memory)
        metadata = dict(item.get("metadata") or {})

        if is_archive_candidate(item):
            metadata["archived"] = True
            metadata["archived_at"] = datetime.now(timezone.utc).isoformat()
            metadata["archive_reason"] = "memory_lifecycle_v1"

        item["metadata"] = metadata
        result.append(item)

    return result


def enforce_active_memory_limit(
    memories: Iterable[Dict[str, Any]],
    max_active: int = ARCHIVE_HARD_LIMIT,
) -> List[Dict[str, Any]]:
    """
    Keep active recall manageable without deleting memory.

    If active memories exceed max_active, lower-ranked active records are marked archived.
    """
    items = mark_archive_candidates(memories)

    active = [
        item for item in items
        if not (item.get("metadata") or {}).get("archived")
    ]

    if len(active) <= max_active:
        return items

    active_sorted = sorted(active, key=lambda m: memory_score(m, query=""), reverse=True)
    keep_ids = {
        item.get("memory_id")
        for item in active_sorted[:max_active]
        if item.get("memory_id")
    }

    result = []
    for item in items:
        metadata = dict(item.get("metadata") or {})
        memory_id = item.get("memory_id")

        if memory_id and memory_id not in keep_ids and not metadata.get("archived"):
            metadata["archived"] = True
            metadata["archived_at"] = datetime.now(timezone.utc).isoformat()
            metadata["archive_reason"] = "active_memory_limit"

        item = dict(item)
        item["metadata"] = metadata
        result.append(item)

    return result
