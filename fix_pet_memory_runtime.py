from pathlib import Path

p = Path("memory_direct_answer.py")
s = p.read_text()

if "def _pet_name_from_text" not in s:
    insert = r'''
def _pet_name_from_text(text):
    import re
    if not text:
        return None
    patterns = [
        r"(?:แมว|หมา|สุนัข|สัตว์เลี้ยง)(?:ของฉัน|ฉัน)?ชื่อ\s*([^\s,\.!?]+)",
        r"(?:แมว|หมา|สุนัข|สัตว์เลี้ยง)(?:ของฉัน|ฉัน)?ชื่อว่า\s*([^\s,\.!?]+)",
        r"(?:ชื่อ(?:แมว|หมา|สุนัข|สัตว์เลี้ยง)(?:ของฉัน)?คือ)\s*([^\s,\.!?]+)",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(1).strip()
    return None


def pet_memory_direct_answer(query, facts=None, memories=None):
    q = query or ""
    if not any(k in q for k in ["แมว", "หมา", "สุนัข", "สัตว์เลี้ยง", "pet"]):
        return None
    if not any(k in q for k in ["ชื่ออะไร", "ชื่อว่าอะไร", "ชื่อ"]):
        return None

    items = []
    if facts:
        if isinstance(facts, dict):
            items += list(facts.values()) + [str(facts)]
        else:
            items += list(facts)
    if memories:
        items += list(memories)

    for item in items:
        if isinstance(item, dict):
            text = " ".join(str(v) for v in item.values())
        else:
            text = str(item)
        name = _pet_name_from_text(text)
        if name:
            return f"สัตว์เลี้ยงของเธอชื่อ{name}"
    return None
'''
    s = insert + "\n" + s

old = "def answer_direct_memory_recall("
idx = s.find(old)
if idx != -1 and "pet_memory_direct_answer(query, facts, memories)" not in s[idx:idx+700]:
    body_start = s.find(":", idx) + 1
    s = s[:body_start] + "\n    pet = pet_memory_direct_answer(query, facts, memories)\n    if pet:\n        return pet\n" + s[body_start:]

p.write_text(s)
print("patched memory_direct_answer.py")
