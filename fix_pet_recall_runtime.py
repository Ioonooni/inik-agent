from pathlib import Path
import re

# 1) Patch facts.py to extract pet_name from "ฉันมีนกชื่อโมจิ"
p = Path("facts.py")
text = p.read_text(encoding="utf-8")

if "pet_name" not in text:
    insert = r'''
    pet_match = re.search(r"(?:ฉันมีนกชื่อ|นกชื่อ|ฉันมีสัตว์เลี้ยงชื่อ|สัตว์เลี้ยงชื่อ)\s*([ก-๙A-Za-z0-9_\-]+)", text)
    if pet_match:
        facts["pet_name"] = pet_match.group(1).strip()
'''
    # place before return facts
    text = text.replace("    return facts", insert + "\n    return facts")

p.write_text(text, encoding="utf-8")
print("patched facts.py pet_name extraction")

# 2) Patch app.py direct memory recall to use broader memories
p = Path("app.py")
text = p.read_text(encoding="utf-8")

old = '''        direct_memory_reply = answer_direct_memory_recall(
            user_message,
            st.session_state.user_facts,
            raw_memories,
        )
        if direct_memory_reply:
            route_decision.direct_reply = direct_memory_reply
'''

new = '''        recall_memories = list(raw_memories or [])
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

if old in text:
    text = text.replace(old, new)
else:
    print("direct memory block not found exactly; no app replacement made")

p.write_text(text, encoding="utf-8")
print("patched app.py broader recall")

# 3) Add no-Gemini regression test
Path("test_pet_recall_runtime.py").write_text(r'''
from facts import extract_facts
from memory_direct_answer import answer_direct_memory_recall
from truth_engine import classify, QueryType

facts = {}
facts = extract_facts("ฉันมีนกชื่อโมจิ", facts)

assert facts.get("pet_name") == "โมจิ", facts

classification = classify("สัตว์เลี้ยงของฉันชื่ออะไร", facts)
assert classification.query_type == QueryType.MEMORY_QUERY, classification

reply = answer_direct_memory_recall(
    "สัตว์เลี้ยงของฉันชื่ออะไร",
    facts,
    [{"content": "ฉันมีนกชื่อโมจิ"}],
)

assert reply is not None
assert "โมจิ" in reply
assert "Gemini" not in reply
assert "ตอบผ่านโมเดลหลักไม่ได้" not in reply

print("PET RECALL RUNTIME TESTS PASSED")
''', encoding="utf-8")

print("patch complete")
