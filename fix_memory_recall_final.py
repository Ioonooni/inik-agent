from pathlib import Path
import re

def write(path, content):
    Path(path).write_text(content, encoding="utf-8")
    print(f"wrote {path}")

# 1) Create deterministic direct memory recall layer
write("memory_direct_answer.py", r'''
import re
from typing import Any, Dict, Iterable, Optional


PET_QUESTION_WORDS = (
    "สัตว์เลี้ยงของฉันชื่ออะไร",
    "สัตว์เลี้ยงฉันชื่ออะไร",
    "นกของฉันชื่ออะไร",
    "นกฉันชื่ออะไร",
)

NAME_QUESTION_WORDS = (
    "ฉันชื่ออะไร",
    "ชื่อฉันคืออะไร",
    "ชื่อของฉันคืออะไร",
)

LIKE_QUESTION_WORDS = (
    "ฉันชอบอะไร",
    "ฉันชอบอะไรบ้าง",
)


def _memory_texts(raw_memories: Iterable[Any]) -> list[str]:
    texts = []
    for item in raw_memories or []:
        if isinstance(item, dict):
            content = item.get("content") or item.get("memory") or item.get("text") or ""
        else:
            content = str(item)
        if content:
            texts.append(str(content))
    return texts


def _find_pet_name(texts: list[str]) -> Optional[str]:
    patterns = [
        r"ฉันมีนกชื่อ\s*([ก-๙A-Za-z0-9_\-]+)",
        r"นกชื่อ\s*([ก-๙A-Za-z0-9_\-]+)",
        r"สัตว์เลี้ยง(?:ของฉัน)?ชื่อ\s*([ก-๙A-Za-z0-9_\-]+)",
        r"ฉันมีสัตว์เลี้ยงชื่อ\s*([ก-๙A-Za-z0-9_\-]+)",
    ]

    for text in reversed(texts):
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()
    return None


def answer_direct_memory_recall(
    user_message: str,
    user_facts: Dict[str, Any] | None = None,
    raw_memories: Iterable[Any] | None = None,
) -> Optional[str]:
    text = (user_message or "").strip().lower()
    facts = user_facts or {}
    memories = _memory_texts(raw_memories or [])

    if any(q in text for q in PET_QUESTION_WORDS) or ("สัตว์เลี้ยง" in text and "ชื่อ" in text):
        pet = facts.get("pet_name") or facts.get("pet") or _find_pet_name(memories)
        if pet:
            return f"เท่าที่ฉันจำได้ สัตว์เลี้ยงของเธอชื่อ {pet}"

    if any(q in text for q in NAME_QUESTION_WORDS):
        name = facts.get("name")
        if name:
            return f"เธอชื่อ {name} ไง"

    if any(q in text for q in LIKE_QUESTION_WORDS):
        likes = facts.get("likes")
        if likes:
            return f"เท่าที่ฉันจำได้ เธอชอบ {likes}"

    return None
''')

# 2) Patch truth_engine memory phrases for pet recall
p = Path("truth_engine.py")
text = p.read_text(encoding="utf-8")

if "สัตว์เลี้ยงของฉันชื่ออะไร" not in text:
    text = text.replace(
        '"ฉันชอบอะไร", "ชอบอะไรบ้าง", "ฉันไม่ชอบอะไร",',
        '"ฉันชอบอะไร", "ชอบอะไรบ้าง", "ฉันไม่ชอบอะไร",\n    "สัตว์เลี้ยงของฉันชื่ออะไร", "สัตว์เลี้ยงฉันชื่ออะไร", "นกของฉันชื่ออะไร", "นกฉันชื่ออะไร",'
    )

p.write_text(text, encoding="utf-8")
print("patched truth_engine.py")

# 3) Patch memory_quality to store pet facts if possible
p = Path("memory_quality.py")
text = p.read_text(encoding="utf-8")

if "pet fact worth storing" not in text:
    marker = "text = (message or \"\").strip().lower()"
    if marker in text:
        insert = '''
    if "มีนกชื่อ" in text or "สัตว์เลี้ยง" in text:
        return MemoryQualityDecision(
            should_store=True,
            memory_type="user_fact",
            importance=75,
            reason="pet fact worth storing",
        )
'''
        text = text.replace(marker, marker + "\n" + insert)

p.write_text(text, encoding="utf-8")
print("patched memory_quality.py")

# 4) Patch app.py: direct memory recall before Gemini/fallback
p = Path("app.py")
text = p.read_text(encoding="utf-8")

if "from memory_direct_answer import answer_direct_memory_recall" not in text:
    text = text.replace(
        "import streamlit as st",
        "import streamlit as st\nfrom memory_direct_answer import answer_direct_memory_recall"
    )

needle = "# 5. Execute routing decision"
insert = '''
        direct_memory_reply = answer_direct_memory_recall(
            user_message,
            st.session_state.user_facts,
            raw_memories,
        )
        if direct_memory_reply:
            route_decision.direct_reply = direct_memory_reply

'''
if needle in text and "direct_memory_reply = answer_direct_memory_recall" not in text:
    text = text.replace(needle, insert + "        " + needle)

p.write_text(text, encoding="utf-8")
print("patched app.py")

# 5) Add deterministic no-Gemini test
write("test_memory_direct_answer.py", r'''
from memory_direct_answer import answer_direct_memory_recall
from truth_engine import classify, QueryType
from memory_quality import assess_memory_quality

facts = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}
memories = [{"content": "ฉันมีนกชื่อโมจิ"}]

reply = answer_direct_memory_recall("สัตว์เลี้ยงของฉันชื่ออะไร", facts, memories)
assert reply is not None
assert "โมจิ" in reply

reply2 = answer_direct_memory_recall("นกของฉันชื่ออะไร", facts, memories)
assert reply2 is not None
assert "โมจิ" in reply2

c = classify("สัตว์เลี้ยงของฉันชื่ออะไร", facts)
assert c.query_type == QueryType.MEMORY_QUERY, c

q = assess_memory_quality("ฉันมีนกชื่อโมจิ")
assert q.should_store is True, q

print("MEMORY DIRECT ANSWER TESTS PASSED")
''')

print("PATCH COMPLETE")
