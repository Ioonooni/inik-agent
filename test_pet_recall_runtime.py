
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
