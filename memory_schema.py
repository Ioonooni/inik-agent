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


# ---------------------------------------------------------------------------
# Conflict detection (Phase 3.4A) — detection only, no mutation
# ---------------------------------------------------------------------------

_CONFLICT_CATEGORIES: list[tuple[str, tuple[str, ...]]] = [
    ("name",     ("ฉันชื่อ", "ชื่อฉันคือ", "ผมชื่อ", "หนูชื่อ", "ชื่อผมคือ", "ชื่อหนูคือ")),
    ("dislike",  ("ฉันไม่ชอบ", "ผมไม่ชอบ", "หนูไม่ชอบ")),
    ("preference", ("ฉันชอบ", "ผมชอบ", "หนูชอบ", "ฉันสนใจ", "เราสนใจ", "ผมสนใจ", "หนูสนใจ")),
    ("study",    ("ฉันกำลังเรียน", "ฉันกำลังศึกษา", "เรากำลังเรียน", "เรากำลังศึกษา",
                  "ผมกำลังเรียน", "ผมกำลังศึกษา", "หนูกำลังเรียน", "หนูกำลังศึกษา")),
    ("project",  ("ฉันกำลังทำ", "เรากำลังทำ", "ผมกำลังทำ", "หนูกำลังทำ")),
    ("location", ("ฉันอยู่", "ฉันอาศัย", "ผมอยู่", "หนูอยู่")),
    ("pet_or_possession", ("ฉันมี", "ผมมี", "หนูมี", "เรามี")),
]

_CONFLICTABLE_TYPES = {"user_fact", "preference"}


def _classify_category(content: str) -> str:
    text = (content or "").strip().lower()
    for category, prefixes in _CONFLICT_CATEGORIES:
        if any(text.startswith(p) for p in prefixes):
            return category
    return "unknown"


def _winner_by_timestamp(existing: Dict[str, Any], incoming: Dict[str, Any]) -> str:
    try:
        ts_e = existing.get("last_seen_at") or existing.get("created_at")
        ts_i = incoming.get("last_seen_at") or incoming.get("created_at")
        if not ts_e or not ts_i:
            return "unknown"
        dt_e = datetime.fromisoformat(str(ts_e).replace("Z", "+00:00"))
        dt_i = datetime.fromisoformat(str(ts_i).replace("Z", "+00:00"))
        if dt_i > dt_e:
            return "incoming"
        if dt_e > dt_i:
            return "existing"
        return "unknown"
    except Exception:
        return "unknown"


def detect_memory_conflict(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Classify whether two memory dicts may conflict. Never mutates either record."""

    def _no(reason: str) -> Dict[str, Any]:
        return {"conflict": False, "reason": reason, "category": None, "winner": "unknown"}

    e_type = (existing.get("memory_type") or "").strip().lower()
    i_type = (incoming.get("memory_type") or "").strip().lower()
    if e_type not in _CONFLICTABLE_TYPES or i_type not in _CONFLICTABLE_TYPES:
        return _no("non-conflictable memory type")

    if existing.get("user_id") != incoming.get("user_id"):
        return _no("different users")

    e_content = (existing.get("content") or "").strip().lower()
    i_content = (incoming.get("content") or "").strip().lower()

    e_cat = _classify_category(e_content)
    i_cat = _classify_category(i_content)

    if e_cat == "unknown" or i_cat == "unknown":
        return _no("unknown category")

    if e_cat != i_cat:
        return _no("different categories")

    if e_content == i_content:
        return _no("identical content")

    return {
        "conflict": True,
        "reason": f"conflicting {e_cat} facts",
        "category": e_cat,
        "winner": _winner_by_timestamp(existing, incoming),
    }


def mark_memory_superseded(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of existing marked superseded when conflict is true and incoming wins.

    Never mutates either input dict. Returns an unchanged copy if no conflict or
    if existing is the winner.
    """
    result = dict(existing)

    conflict = detect_memory_conflict(existing, incoming)
    if not conflict["conflict"] or conflict["winner"] != "incoming":
        return result

    meta = dict(result.get("metadata") or {})
    meta["superseded"] = True
    meta["superseded_by"] = incoming.get("memory_id")
    meta["superseded_at"] = utc_now_iso()
    meta["superseded_category"] = conflict["category"]
    result["metadata"] = meta
    return result


def merge_duplicate_memory(existing: Dict[str, Any], incoming: MemoryRecord) -> Dict[str, Any]:
    merged = dict(existing)
    merged["last_seen_at"] = incoming.last_seen_at
    new_hit_count = int(merged.get("hit_count", 1)) + 1
    merged["hit_count"] = new_hit_count
    base_importance = max(int(merged.get("importance", 0)), incoming.importance)
    reinforcement_bonus = min(20, max(0, new_hit_count - 1) * 2)
    merged["importance"] = min(100, base_importance + reinforcement_bonus)
    merged["schema_version"] = SCHEMA_VERSION
    meta = dict(merged.get("metadata") or {})
    meta["reinforced"] = True
    meta["reinforcement_bonus"] = reinforcement_bonus
    merged["metadata"] = meta
    return merged
