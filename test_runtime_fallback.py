
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
