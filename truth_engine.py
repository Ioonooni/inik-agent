from dataclasses import dataclass
from typing import Any, Dict, Optional

from confidence import MemoryConfidence, score_fact_reliability


_LIVE_DATA_WORDS = {
    "อากาศ", "weather", "ฝน", "ร้อน", "หนาว", "พยากรณ์",
    "ราคา", "หุ้น", "ข่าว", "ล่าสุด", "ตอนนี้", "วันนี้", "เดี๋ยวนี้",
    "เวลา", "นาฬิกา", "วันที่", "เดือน", "ปี", "ปฏิทิน",
    "ตลาด", "bitcoin", "crypto", "เรตแลกเปลี่ยน",
}

_MEMORY_WORDS = {
    "ชื่อ", "ชอบ", "ไม่ชอบ", "จำได้", "จำ", "รู้ว่า", "รู้จัก",
    "บอกว่า", "เคยบอก", "เคยพูด",
}

_RELATIONSHIP_WORDS = {
    "สนิท", "ความสัมพันธ์", "trust", "familiarity", "curiosity",
    "รู้สึกไง", "คิดถึง", "ชอบฉัน",
}

_TOOL_WORDS = {
    "คะแนน", "แต้ม", "point", "points",
    "inventory", "ไอเท็ม", "ของใน inventory", "ดูของ",
    "stage", "เลเวล",
}


class QueryType:
    MEMORY_QUERY = "MEMORY_QUERY"
    FACTUAL_QUERY = "FACTUAL_QUERY"
    NORMAL_CHAT = "NORMAL_CHAT"
    TOOL_QUERY = "TOOL_QUERY"
    RELATIONSHIP_QUERY = "RELATIONSHIP_QUERY"


@dataclass
class QueryClassification:
    query_type: str
    confidence: MemoryConfidence
    memory_key: Optional[str] = None
    requires_live_data: bool = False
    can_answer_directly: bool = False


def _detect_memory_key(text: str) -> Optional[str]:
    if any(w in text for w in ["ชื่อ", "name"]):
        return "name"
    if any(w in text for w in ["ชอบ", "likes"]):
        return "likes"
    return None


def classify(user_message: str, user_facts: Dict[str, Any]) -> QueryClassification:
    text = (user_message or "").lower().strip()

    if any(w in text for w in _LIVE_DATA_WORDS):
        return QueryClassification(
            query_type=QueryType.FACTUAL_QUERY,
            confidence=MemoryConfidence.UNKNOWN,
            requires_live_data=True,
            can_answer_directly=False,
        )

    if any(w in text for w in _TOOL_WORDS):
        return QueryClassification(
            query_type=QueryType.TOOL_QUERY,
            confidence=MemoryConfidence.HIGH,
            can_answer_directly=True,
        )

    if any(w in text for w in _RELATIONSHIP_WORDS):
        return QueryClassification(
            query_type=QueryType.RELATIONSHIP_QUERY,
            confidence=MemoryConfidence.HIGH,
            can_answer_directly=True,
        )

    if any(w in text for w in _MEMORY_WORDS):
        memory_key = _detect_memory_key(text)

        if memory_key and user_facts.get(memory_key):
            conf = score_fact_reliability(user_facts, memory_key)
        elif user_facts:
            conf = MemoryConfidence.MEDIUM
        else:
            conf = MemoryConfidence.UNKNOWN

        return QueryClassification(
            query_type=QueryType.MEMORY_QUERY,
            confidence=conf,
            memory_key=memory_key,
            requires_live_data=False,
            can_answer_directly=bool(memory_key and user_facts.get(memory_key)),
        )

    return QueryClassification(
        query_type=QueryType.NORMAL_CHAT,
        confidence=MemoryConfidence.MEDIUM,
        can_answer_directly=False,
    )
