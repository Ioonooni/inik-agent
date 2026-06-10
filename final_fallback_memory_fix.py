from pathlib import Path
import re

BAD_PATTERNS = [
    "ขอโทษนะ ตอนนี้ i nik ตอบผ่านโมเดลหลักไม่ได้ชั่วคราว ฉันจะไม่เดาข้อมูลแทนสักครู่นะ",
    "ขอโทษนะ ตอนนี้ i nik เชื่อมต่อ Gemini ไม่ได้ชั่วคราว ลองถามใหม่อีกครั้งนะ",
    "ตอบผ่านโมเดลหลักไม่ได้ชั่วคราว ฉันจะไม่เดาข้อมูลแทนสักครู่นะ",
    "เชื่อมต่อ Gemini ไม่ได้",
    "ลองถามใหม่",
]

GOOD_NORMAL = "รับรู้แล้วนะ ฉันยังตอบแบบโมเดลหลักไม่ได้เต็มที่ตอนนี้ แต่จะไม่เดาข้อมูลหรือดึงความจำมั่ว ๆ แทน"

# 1) Replace bad fallback wording everywhere except tests/docs/cache/git
for path in Path(".").glob("*.py"):
    if path.name.startswith("test_"):
        continue
    if path.name in {"final_fallback_memory_fix.py"}:
        continue

    text = path.read_text(encoding="utf-8")
    old_text = text

    for bad in BAD_PATTERNS:
        text = text.replace(bad, GOOD_NORMAL)

    # clean awkward leftover wording
    text = text.replace("สักครู่นะ", "")
    text = text.replace("ขอโทษนะ ตอนนี้ i nik " + GOOD_NORMAL, GOOD_NORMAL)

    if text != old_text:
        path.write_text(text, encoding="utf-8")
        print("patched", path)

# 2) Make runtime_fallback normal chat never use apology/retry style
runtime = Path("runtime_fallback.py")
if runtime.exists():
    text = runtime.read_text(encoding="utf-8")
    text = re.sub(
        r'return\s+"[^"]*ตอบผ่านโมเดลหลักไม่ได้ชั่วคราว[^"]*"',
        f'return "{GOOD_NORMAL}"',
        text,
    )
    text = text.replace("สักครู่นะ", "")
    runtime.write_text(text, encoding="utf-8")
    print("hardened runtime_fallback.py")

# 3) Make fallback.py never expose Gemini/retry wording
fallback = Path("fallback.py")
if fallback.exists():
    text = fallback.read_text(encoding="utf-8")
    text = text.replace("Gemini", "โมเดลหลัก")
    text = text.replace("ลองถามใหม่", "ฉันจะไม่เดาข้อมูลแทน")
    text = text.replace("สักครู่นะ", "")
    fallback.write_text(text, encoding="utf-8")
    print("hardened fallback.py")

# 4) Strengthen memory direct answer for pet recall
mem_direct = Path("memory_direct_answer.py")
if mem_direct.exists():
    text = mem_direct.read_text(encoding="utf-8")
    if "สัตว์เลี้ยงของฉันชื่ออะไร" in text and "โมเดลหลัก" not in text:
        pass
else:
    mem_direct.write_text('''
import re
from typing import Any, Dict, Iterable, Optional

def _texts(raw_memories):
    out = []
    for item in raw_memories or []:
        if isinstance(item, dict):
            out.append(str(item.get("content") or item.get("memory") or item.get("text") or ""))
        else:
            out.append(str(item))
    return [x for x in out if x]

def _find_pet(texts):
    pats = [
        r"ฉันมีนกชื่อ\\s*([ก-๙A-Za-z0-9_\\-]+)",
        r"นกชื่อ\\s*([ก-๙A-Za-z0-9_\\-]+)",
        r"ฉันมีสัตว์เลี้ยงชื่อ\\s*([ก-๙A-Za-z0-9_\\-]+)",
        r"สัตว์เลี้ยงชื่อ\\s*([ก-๙A-Za-z0-9_\\-]+)",
    ]
    for t in reversed(texts):
        for p in pats:
            m = re.search(p, t)
            if m:
                return m.group(1).strip()
    return None

def answer_direct_memory_recall(user_message: str, user_facts: Dict[str, Any] | None = None, raw_memories: Iterable[Any] | None = None) -> Optional[str]:
    text = (user_message or "").strip().lower()
    facts = user_facts or {}
    memories = _texts(raw_memories or [])

    if ("สัตว์เลี้ยง" in text and "ชื่อ" in text) or ("นก" in text and "ชื่อ" in text):
        pet = facts.get("pet_name") or facts.get("pet") or _find_pet(memories)
        if pet:
            return f"เท่าที่ฉันจำได้ สัตว์เลี้ยงของเธอชื่อ {pet}"

    if "ชื่อ" in text and "ฉัน" in text:
        name = facts.get("name")
        if name:
            return f"เธอชื่อ {name} ไง"

    if "ชอบอะไร" in text:
        likes = facts.get("likes")
        if likes:
            return f"เท่าที่ฉันจำได้ เธอชอบ {likes}"

    return None
''', encoding="utf-8")
    print("created memory_direct_answer.py")

# 5) Ensure app.py imports and uses direct memory recall before fallback/Gemini branch
app = Path("app.py")
text = app.read_text(encoding="utf-8")

if "from memory_direct_answer import answer_direct_memory_recall" not in text:
    text = text.replace(
        "import streamlit as st",
        "import streamlit as st\nfrom memory_direct_answer import answer_direct_memory_recall"
    )

if "direct_memory_reply = answer_direct_memory_recall(" not in text:
    needle = "# 5. Execute routing decision"
    block = '''        recall_memories = list(raw_memories or [])
        try:
            broader_memories = get_raw_memories(
                user_id=user_id,
                user_message="",
                limit=50,
            )
            recall_memories.extend(broader_memories or [])
        except Exception:
            pass

        direct_memory_reply = answer_direct_memory_recall(
            user_message,
            st.session_state.user_facts,
            recall_memories,
        )
        if direct_memory_reply:
            route_decision.direct_reply = direct_memory_reply

'''
    text = text.replace(needle, block + "        " + needle)

app.write_text(text, encoding="utf-8")
print("hardened app.py")

# 6) Add final test
Path("test_final_memory_recall_no_fallback.py").write_text(f'''
from memory_direct_answer import answer_direct_memory_recall
from runtime_fallback import build_runtime_fallback

facts = {{"pet_name": "โมจิ", "name": "ไออุ่น", "likes": "ดาวเสาร์"}}
memories = [{{"content": "ฉันมีนกชื่อโมจิ"}}]

reply = answer_direct_memory_recall("สัตว์เลี้ยงของฉันชื่ออะไร", facts, memories)
assert reply is not None
assert "โมจิ" in reply
assert "Gemini" not in reply
assert "โมเดลหลักไม่ได้" not in reply

fallback = build_runtime_fallback("วันนี้กินข้าวไข่เจียวตอน 13:17 น.", None)
assert "ลองถามใหม่" not in fallback
assert "เชื่อมต่อ Gemini" not in fallback
assert "สักครู่นะ" not in fallback

print("FINAL MEMORY RECALL NO FALLBACK TESTS PASSED")
''', encoding="utf-8")

print("FINAL PATCH COMPLETE")
