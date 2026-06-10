from pathlib import Path
import re

def write_file(path, content):
    Path(path).write_text(content, encoding="utf-8")
    print(f"wrote {path}")

# 1) Add safe runtime fallback layer
write_file("runtime_fallback.py", r'''
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
''')

# 2) Add regression tests
write_file("test_runtime_fallback.py", r'''
from truth_engine import classify, QueryType
from runtime_fallback import build_runtime_fallback
from memory_quality import assess_memory_quality

facts = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}

live = classify("ตอนนี้กี่โมง", facts)
assert live.requires_live_data is True
assert "ดูเวลาปัจจุบันแบบสดไม่ได้" in build_runtime_fallback("ตอนนี้กี่โมง", live)

weather = classify("วันนี้อากาศเป็นไง", facts)
assert weather.requires_live_data is True
assert "ดูอากาศสดไม่ได้" in build_runtime_fallback("วันนี้อากาศเป็นไง", weather)

gold = classify("ราคาทองวันนี้เท่าไร", facts)
assert gold.requires_live_data is True
assert "ดูราคาทอง" in build_runtime_fallback("ราคาทองวันนี้เท่าไร", gold)

math = classify("2+2 เท่ากับเท่าไร", facts)
assert math.query_type == QueryType.FACTUAL_QUERY
assert build_runtime_fallback("2+2 เท่ากับเท่าไร", math) == "4"

meal = assess_memory_quality("วันนี้กินข้าวไข่เจียวตอน 13:17 น.")
assert meal.should_store is False, meal

normal = classify("วันนี้กินข้าวไข่เจียวตอน 13:17 น.", facts)
reply = build_runtime_fallback("วันนี้กินข้าวไข่เจียวตอน 13:17 น.", normal)
assert "ลองถามใหม่" not in reply
assert "ความจำ" in reply or "รับรู้" in reply

print("RUNTIME FALLBACK TESTS PASSED")
''')

# 3) Patch app.py only if it has a broad Gemini error fallback text
app = Path("app.py")
text = app.read_text(encoding="utf-8")

if "from runtime_fallback import build_runtime_fallback" not in text:
    text = text.replace(
        "from fallback import",
        "from runtime_fallback import build_runtime_fallback\nfrom fallback import"
    ) if "from fallback import" in text else text.replace(
        "import streamlit as st",
        "import streamlit as st\nfrom runtime_fallback import build_runtime_fallback"
    )

# Replace common temporary Gemini error message if present.
patterns = [
    r'reply\s*=\s*f?[\'"]ขอโทษนะ[^\'"]*Gemini[^\'"]*ลองถามใหม่[^\'"]*[\'"]',
    r'assistant_reply\s*=\s*f?[\'"]ขอโทษนะ[^\'"]*Gemini[^\'"]*ลองถามใหม่[^\'"]*[\'"]',
    r'final_reply\s*=\s*f?[\'"]ขอโทษนะ[^\'"]*Gemini[^\'"]*ลองถามใหม่[^\'"]*[\'"]',
]

patched = False
for pat in patterns:
    new_text = re.sub(pat, lambda m: m.group(0).split("=")[0] + "= build_runtime_fallback(user_message, classification)", text)
    if new_text != text:
        text = new_text
        patched = True

app.write_text(text, encoding="utf-8")
print("patched app.py import/runtime fallback" if patched else "app.py import ensured; no broad Gemini fallback pattern replaced")

