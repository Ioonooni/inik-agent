
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
