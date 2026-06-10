import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from memory_schema import merge_duplicate_memory


DEFAULT_MEMORY_V2_PATH = "memory_store_v2.json"


def _load_raw(path: str = DEFAULT_MEMORY_V2_PATH) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"schema": "memory_store_v2", "memories": []}

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema": "memory_store_v2", "memories": []}

    if not isinstance(data, dict):
        return {"schema": "memory_store_v2", "memories": []}

    if "memories" not in data or not isinstance(data["memories"], list):
        data["memories"] = []

    data["schema"] = "memory_store_v2"
    return data


def _save_raw(data: Dict[str, Any], path: str = DEFAULT_MEMORY_V2_PATH) -> None:
    p = Path(path)
    p.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def list_memories(
    user_id: Optional[str] = None,
    path: str = DEFAULT_MEMORY_V2_PATH,
) -> List[Dict[str, Any]]:
    data = _load_raw(path)
    memories = data.get("memories", [])

    if user_id is None:
        return list(memories)

    return [m for m in memories if m.get("user_id") == user_id]


def upsert_memory_record(
    record: Dict[str, Any],
    path: str = DEFAULT_MEMORY_V2_PATH,
) -> Dict[str, Any]:
    if not record.get("memory_id"):
        raise ValueError("record must include memory_id")

    data = _load_raw(path)
    memories = data["memories"]

    for idx, existing in enumerate(memories):
        if existing.get("memory_id") == record["memory_id"]:
            merged = merge_duplicate_memory(existing, _record_like(record))
            memories[idx] = merged
            _save_raw(data, path)
            return {"ok": True, "action": "merged", "record": merged}

    memories.append(record)
    _save_raw(data, path)
    return {"ok": True, "action": "inserted", "record": record}


class _record_like:
    def __init__(self, record: Dict[str, Any]):
        self.last_seen_at = record.get("last_seen_at")
        self.importance = int(record.get("importance", 0))


def search_memories(
    query: str,
    user_id: Optional[str] = None,
    path: str = DEFAULT_MEMORY_V2_PATH,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    q = (query or "").strip().lower()
    if not q:
        return []

    memories = list_memories(user_id=user_id, path=path)

    scored = []
    for memory in memories:
        content = (memory.get("content") or "").lower()
        memory_type = (memory.get("memory_type") or "").lower()

        score = 0
        if q in content:
            score += 10
        if q in memory_type:
            score += 3

        score += int(memory.get("importance", 0)) / 100
        score += int(memory.get("hit_count", 1)) * 0.1

        if score > 0:
            scored.append((score, memory))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [m for _, m in scored[:limit]]


def reset_memory_store(path: str = DEFAULT_MEMORY_V2_PATH) -> None:
    _save_raw({"schema": "memory_store_v2", "memories": []}, path)
