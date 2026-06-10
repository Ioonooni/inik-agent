
from truth_engine import classify, QueryType
from runtime_fallback import build_runtime_fallback
from memory_direct_answer import answer_direct_memory_recall

facts = {"pet_name": "โมจิ", "name": "ไออุ่น", "likes": "ดาวเสาร์"}
memories = [{"content": "ฉันมีนกชื่อโมจิ"}]

classification = classify("สัตว์เลี้ยงของฉันชื่ออะไร", facts)
assert classification.query_type == QueryType.MEMORY_QUERY, classification

direct = answer_direct_memory_recall("สัตว์เลี้ยงของฉันชื่ออะไร", facts, memories)
assert direct is not None and "โมจิ" in direct

fallback = build_runtime_fallback(
    "สัตว์เลี้ยงของฉันชื่ออะไร",
    classification,
    facts,
    memories,
)
assert "โมจิ" in fallback, fallback
assert "โมเดลหลักไม่ได้" not in fallback, fallback
assert "Gemini" not in fallback, fallback
assert "ลองถามใหม่" not in fallback, fallback

print("RUNTIME MEMORY RECALL END TO END TESTS PASSED")
