import re
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


_FACT_MARKERS = ("ชื่อว่า", "ชื่อคือ", "อายุ", "อยู่ที่", "เกิดที่", "ทำงาน", "เรียนที่")
_PREFERENCE_MARKERS = ("ชอบ", "ไม่ชอบ", "โปรด", "หลงรัก", "เกลียด")
_EVENT_MARKERS = ("เจอกับ", "ไปที่", "กินที่", "ดูแล้ว", "เล่นแล้ว", "วันนี้ได้", "เมื่อวาน")

# Imperative / command verbs at the start of a stored entry signal a user query echo
_QUERY_STARTERS = (
    "เล่า", "บอก", "อธิบาย", "สอน", "แนะนำ",
    "ช่วย", "ลอง", "เขียน", "สร้าง", "แต่ง",
    "คิด", "วิเคราะห์", "สรุป", "ยก",
)

# Question endings that mark a stored entry as a user query
_QUESTION_ENDINGS = (
    "คืออะไร", "ไหม", "หรือเปล่า",
    "ยังไง", "อย่างไร",
    "เท่าไร", "เท่าไหร่",
    "คืออะไร", "กี่อย่าง",
)

# Math expression
_MATH_RE = re.compile(r'^[\d\s\+\-\*\/\=\(\)\.]+$')


def _is_query_like(content: str) -> bool:
    """Return True if this content looks like a stored user request rather than a fact."""
    stripped = content.strip().lower()

    if any(stripped.startswith(v) for v in _QUERY_STARTERS):
        return True

    if any(stripped.endswith(q) for q in _QUESTION_ENDINGS):
        return True

    if "?" in content:
        return True

    if _MATH_RE.match(stripped):
        return True

    return False


def _classify_entry_type(content: str) -> str:
    # Query-like content is always an echo — check this first
    if _is_query_like(content):
        return EntryType.CONVERSATION_ECHO

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

    # Raw system dump: "[user_message] text (ISO-date)"
    if stripped.startswith("[") and "]" in stripped:
        return True

    return False


def verify(entries: List[Dict[str, Any]]) -> List[VerifiedMemory]:
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

        # Echoes are never high-confidence context
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
