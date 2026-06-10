
from memory_direct_answer import answer_direct_memory_recall
from runtime_fallback import build_runtime_fallback

facts = {"pet_name": "โมจิ", "name": "ไออุ่น", "likes": "ดาวเสาร์"}
memories = [{"content": "ฉันมีนกชื่อโมจิ"}]

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
