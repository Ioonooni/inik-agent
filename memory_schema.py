from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, Optional


SCHEMA_VERSION = "memory_v2"


@dataclass
class MemoryRecord:
    memory_id: str
    user_id: str
    content: str
    memory_type: str
    importance: int
    source: str
    schema_version: str
    created_at: str
    last_seen_at: str
    hit_count: int
    metadata: Dict[str, Any]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_memory_id(user_id: str, content: str, memory_type: str) -> str:
    raw = f"{user_id}|{memory_type}|{content.strip().lower()}"
    return sha256(raw.encode("utf-8")).hexdigest()[:24]


def build_memory_record(
    user_id: str,
    content: str,
    memory_type: str,
    importance: int,
    source: str = "chat",
    metadata: Optional[Dict[str, Any]] = None,
) -> MemoryRecord:
    clean_content = (content or "").strip()
    if not clean_content:
        raise ValueError("content cannot be empty")

    safe_importance = max(0, min(100, int(importance)))
    now = utc_now_iso()

    return MemoryRecord(
        memory_id=make_memory_id(user_id, clean_content, memory_type),
        user_id=user_id,
        content=clean_content,
        memory_type=memory_type,
        importance=safe_importance,
        source=source,
        schema_version=SCHEMA_VERSION,
        created_at=now,
        last_seen_at=now,
        hit_count=1,
        metadata=metadata or {},
    )


def record_to_dict(record: MemoryRecord) -> Dict[str, Any]:
    return asdict(record)


def should_promote_to_long_term(record: MemoryRecord) -> bool:
    if record.memory_type in ("user_fact", "preference"):
        return record.importance >= 60
    if record.memory_type == "emotional_event":
        return record.importance >= 70
    return record.importance >= 80


def merge_duplicate_memory(existing: Dict[str, Any], incoming: MemoryRecord) -> Dict[str, Any]:
    merged = dict(existing)
    merged["last_seen_at"] = incoming.last_seen_at
    merged["hit_count"] = int(merged.get("hit_count", 1)) + 1
    merged["importance"] = max(int(merged.get("importance", 0)), incoming.importance)
    merged["schema_version"] = SCHEMA_VERSION
    return merged
