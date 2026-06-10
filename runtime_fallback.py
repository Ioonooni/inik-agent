
from typing import Any


def _qtype_name(classification: Any) -> str:
    return str(getattr(classification, "query_type", "") or "")


def _is_live_data(classification: Any) -> bool:
    return bool(getattr(classification, "requires_live_data", False))


def build_runtime_fallback(user_message: str, classification: Any = None) -> str:
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
        return "ตอนนี้ฉันตอบจากโมเดลหลักไม่ได้ชั่วคราว แต่คำถามนี้เป็นคำถามความรู้ ไม่ใช่ข้อมูลความจำของเธอ"

    if "MEMORY_QUERY" in qtype:
        return "ตอนนี้ฉันตรวจความจำระยะยาวไม่ได้ชั่วคราว แต่จะไม่เดาข้อมูลแทนความจำจริง"

    if "TOOL_QUERY" in qtype or "RELATIONSHIP_QUERY" in qtype:
        return "ตอนนี้ฉันอ่านสถานะระบบไม่ได้ชั่วคราว เลยยังไม่ควรเดาค่าระบบให้เธอ"

    # Normal chat fallback: no system dump, no retry loop, still character-safe.
    if any(w in text for w in ("เหนื่อย", "ไม่ไหว", "เครียด", "เศร้า")):
        return "ได้ยินนะ วันนี้ดูหนักอยู่เหมือนกัน พักหายใจก่อนก็ได้ ไม่ต้องรีบจัดการทุกอย่างพร้อมกัน"

    if text:
        return "รับรู้แล้วนะ ฉันยังตอบแบบโมเดลหลักไม่ได้เต็มที่ตอนนี้ แต่ข้อความนี้ไม่ควรถูกบันทึกเป็นความจำมั่ว ๆ"

    return "ตอนนี้ฉันตอบไม่ได้เต็มที่ชั่วคราว"
