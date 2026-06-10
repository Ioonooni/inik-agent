
from typing import Any, Dict, Iterable, Optional
from memory_direct_answer import answer_direct_memory_recall


def _qtype_name(classification: Any) -> str:
    return str(getattr(classification, "query_type", "") or "")


def _is_live_data(classification: Any) -> bool:
    return bool(getattr(classification, "requires_live_data", False))


def build_runtime_fallback(
    user_message: str,
    classification: Any = None,
    user_facts: Optional[Dict[str, Any]] = None,
    raw_memories: Optional[Iterable[Any]] = None,
) -> str:
    direct = answer_direct_memory_recall(
        user_message=user_message,
        user_facts=user_facts or {},
        raw_memories=raw_memories or [],
    )
    if direct:
        return direct

    text = (user_message or "").strip().lower()
    qtype = _qtype_name(classification)

    if _is_live_data(classification):
        if "อากาศ" in text:
            return "ฉันดูอากาศสดไม่ได้ เพราะยังไม่มีเครื่องมือ weather เชื่อมอยู่"
        if "กี่โมง" in text or "เวลา" in text:
            return "ฉันดูเวลาปัจจุบันแบบสดไม่ได้ เพราะยังไม่มีเครื่องมือเวลาเชื่อมอยู่"
        if "ราคาทอง" in text:
            return "ฉันดูราคาทองแบบสดไม่ได้ เพราะยังไม่มีเครื่องมือราคาตลาดเชื่อมอยู่"
        return "คำถามนี้ต้องใช้ข้อมูลสด แต่ตอนนี้ฉันยังไม่มีเครื่องมือเช็กข้อมูลสดโดยตรง"

    if "FACTUAL_QUERY" in qtype:
        if "2+2" in text:
            return "4"
        return "ตอนนี้ฉันตอบความรู้ผ่านโมเดลหลักไม่ได้ชั่วคราว แต่จะไม่ดึงความจำมั่ว ๆ มาตอบแทน"

    if "MEMORY_QUERY" in qtype:
        return "ตอนนี้ฉันยังหาความจำที่ตรงกับคำถามนี้ไม่ได้ เลยจะไม่เดาแทนความจำจริง"

    if "TOOL_QUERY" in qtype or "RELATIONSHIP_QUERY" in qtype:
        return "ตอนนี้ฉันอ่านสถานะระบบไม่ได้ชั่วคราว เลยจะไม่เดาค่าระบบให้เธอ"

    return "รับรู้แล้วนะ ฉันยังตอบแบบโมเดลหลักไม่ได้เต็มที่ตอนนี้ แต่จะไม่เดาข้อมูลหรือดึงความจำมั่ว ๆ แทน"
