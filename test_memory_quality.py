from memory_quality import assess_memory_quality

cases = [
    ("ฉันชื่อไออุ่น", True, "user_fact"),
    ("ฉันชอบดาวเสาร์", True, "user_fact"),
    ("ฉันชอบอะไรเกี่ยวกับหลุมดำ", False, "question"),
    ("หลุมดำคืออะไร", False, "factual_query"),
    ("2+2 เท่ากับเท่าไร", False, "factual_query"),
    ("ตอนนี้กี่โมง", False, "live_data_query"),
    ("วันนี้อากาศเป็นไง", False, "live_data_query"),
    ("เหนื่อยมากวันนี้", True, "emotional_event"),
    ("คุยเล่นหน่อย", False, "low_value_chat"),
]

for text, should_store, memory_type in cases:
    result = assess_memory_quality(text)
    print(text, "=>", result)
    assert result.should_store == should_store
    assert result.memory_type == memory_type

print("MEMORY QUALITY TESTS PASSED")
