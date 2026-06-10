from enum import Enum
from typing import Any, Dict


class MemoryConfidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


def score_memory_entry(entry: Dict[str, Any]) -> MemoryConfidence:
    content = (entry.get("content") or "").strip()

    if not content or len(content) < 5:
        return MemoryConfidence.UNKNOWN

    if 10 <= len(content) <= 500:
        return MemoryConfidence.HIGH

    if len(content) > 500:
        return MemoryConfidence.MEDIUM

    return MemoryConfidence.LOW


def score_fact_reliability(facts: Dict[str, Any], key: str) -> MemoryConfidence:
    if not facts or key not in facts:
        return MemoryConfidence.UNKNOWN

    value = facts.get(key)
    if not value:
        return MemoryConfidence.UNKNOWN

    history = facts.get("_history", {}).get(key, [])

    if len(history) >= 3:
        recent_values = [h.get("value") for h in history[-3:]]
        if len(set(recent_values)) == 1:
            return MemoryConfidence.HIGH
        return MemoryConfidence.MEDIUM

    if len(history) >= 1:
        return MemoryConfidence.MEDIUM

    return MemoryConfidence.LOW


def to_label(confidence: MemoryConfidence) -> str:
    labels = {
        MemoryConfidence.HIGH: "มั่นใจสูง",
        MemoryConfidence.MEDIUM: "พอจำได้",
        MemoryConfidence.LOW: "ไม่แน่ใจ",
        MemoryConfidence.UNKNOWN: "ไม่รู้",
    }
    return labels.get(confidence, "ไม่รู้")
