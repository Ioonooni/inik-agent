from dataclasses import dataclass
from typing import Any, Dict, List

from confidence import MemoryConfidence, score_memory_entry


class EntryType:
    USER_FACT = "user_fact"
    PREFERENCE = "preference"
    EVENT = "event"
    CONVERSATION_ECHO = "conversation_echo"
    UNCERTAIN_INFERENCE = "uncertain_inference"


@dataclass
class VerifiedMemory:
    content: str
    entry_type: str
    confidence: MemoryConfidence
    original: Dict[str, Any]


_FACT_MARKERS = ["ชื่อ", "อายุ", "อยู่ที่", "เกิด", "ทำงาน", "เรียน"]
_PREFERENCE_MARKERS = ["ชอบ", "ไม่ชอบ", "โปรด", "หลงรัก", "เกลียด"]
_EVENT_MARKERS = ["ไป", "เจอ", "ทำ", "กิน", "ดู", "เล่น", "วันนี้", "เมื่อวาน"]


def _classify_entry_type(content: str) -> str:
    lower = content.lower()

    if any(m in lower for m in _FACT_MARKERS):
        return EntryType.USER_FACT

    if any(m in lower for m in _PREFERENCE_MARKERS):
        return EntryType.PREFERENCE

    if any(m in lower for m in _EVENT_MARKERS):
        return EntryType.EVENT

    if len(content) < 15:
        return EntryType.CONVERSATION_ECHO

    return EntryType.UNCERTAIN_INFERENCE


def _is_low_quality(content: str) -> bool:
    stripped = content.strip()

    if len(stripped) < 5:
        return True

    # Raw system dump pattern: "[user_message] text (ISO-date)"
    if stripped.startswith("[") and "]" in stripped:
        return True

    return False


def verify(entries: List[Dict[str, Any]]) -> List["VerifiedMemory"]:
    seen_contents: set = set()
    result: List[VerifiedMemory] = []

    for entry in entries:
        content = (entry.get("content") or "").strip()

        if not content:
            continue

        if _is_low_quality(content):
            continue

        normalized = content.lower()
        if normalized in seen_contents:
            continue
        seen_contents.add(normalized)

        conf = score_memory_entry(entry)
        etype = _classify_entry_type(content)

        if etype == EntryType.CONVERSATION_ECHO:
            conf = MemoryConfidence.LOW

        result.append(VerifiedMemory(
            content=content,
            entry_type=etype,
            confidence=conf,
            original=entry,
        ))

    _CONF_ORDER = {
        MemoryConfidence.HIGH: 0,
        MemoryConfidence.MEDIUM: 1,
        MemoryConfidence.LOW: 2,
        MemoryConfidence.UNKNOWN: 3,
    }
    _TYPE_PRIORITY = {
        EntryType.USER_FACT: 0,
        EntryType.PREFERENCE: 1,
        EntryType.EVENT: 2,
        EntryType.UNCERTAIN_INFERENCE: 3,
        EntryType.CONVERSATION_ECHO: 4,
    }

    result.sort(key=lambda m: (_CONF_ORDER[m.confidence], _TYPE_PRIORITY[m.entry_type]))

    return result
