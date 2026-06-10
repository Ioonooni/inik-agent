from dataclasses import dataclass


@dataclass
class MemoryQualityDecision:
    should_store: bool
    memory_type: str
    importance: int
    reason: str


QUESTION_MARKERS = (
    "อะไร", "ไหม", "หรือ", "เหรอ", "หรอ", "ยังไง", "อย่างไร",
    "เท่าไหร่", "เท่าไร", "กี่", "?", "คืออะไร", "เล่าเรื่อง",
    "อธิบาย", "ทำไม", "เพราะอะไร"
)

LIVE_DATA_WORDS = (
    "อากาศ", "กี่โมง", "เวลาตอนนี้", "ตอนนี้กี่โมง",
    "ราคาทอง", "ราคาหุ้น", "ราคาน้ำมัน", "ข่าวล่าสุด", "ข่าววันนี้"
)

FACTUAL_WORDS = (
    "คืออะไร", "อธิบาย", "เล่าเรื่อง", "หมายความว่า",
    "ทำงานยังไง", "เกิดขึ้นยังไง", "เพราะอะไร",
    "เท่ากับ", "คำนวณ", "กลมไหม"
)

PERSONAL_FACT_PREFIXES = (
    "ฉันชื่อ", "ชื่อฉันคือ", "ผมชื่อ", "หนูชื่อ",
    "ฉันชอบ", "ผมชอบ", "หนูชอบ",
    "ฉันไม่ชอบ", "ผมไม่ชอบ", "หนูไม่ชอบ",
    "ฉันเกิด", "วันเกิดฉัน", "ฉันอยู่",
)

EMOTIONAL_WORDS = (
    "เหนื่อย", "เศร้า", "ไม่ไหว", "พัง", "ร้องไห้",
    "ดีใจ", "กลัว", "กังวล", "เครียด", "เหงา"
)


def is_question_like(text: str) -> bool:
    clean = (text or "").strip().lower()
    return any(marker in clean for marker in QUESTION_MARKERS)


def assess_memory_quality(content: str) -> MemoryQualityDecision:
    text = (content or "").strip().lower()

    if not text:
        return MemoryQualityDecision(False, "empty", 0, "empty content")

    if any(word in text for word in LIVE_DATA_WORDS):
        return MemoryQualityDecision(False, "live_data_query", 0, "live-data queries should not be stored")

    if any(word in text for word in FACTUAL_WORDS):
        return MemoryQualityDecision(False, "factual_query", 0, "factual questions should not become memory")

    if is_question_like(text):
        return MemoryQualityDecision(False, "question", 0, "questions should not be stored as long-term memory")

    if any(text.startswith(prefix) for prefix in PERSONAL_FACT_PREFIXES):
        return MemoryQualityDecision(True, "user_fact", 80, "explicit personal fact/preference")

    if any(word in text for word in EMOTIONAL_WORDS):
        return MemoryQualityDecision(True, "emotional_event", 60, "emotional signal worth remembering lightly")

    if len(text) >= 80:
        return MemoryQualityDecision(True, "conversation_event", 40, "long user message may contain useful context")

    return MemoryQualityDecision(False, "low_value_chat", 10, "short casual message not worth long-term storage")
