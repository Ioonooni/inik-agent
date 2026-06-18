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


def test_name_importance():
    assert assess_memory_quality("ฉันชื่อไออุ่น").importance == 95
    assert assess_memory_quality("ชื่อฉันคืออุ่น").importance == 95


def test_preference_importance():
    assert assess_memory_quality("ฉันชอบดาวเสาร์").importance == 85
    assert assess_memory_quality("ฉันไม่ชอบเสียงดัง").importance == 85


def test_named_possession_importance():
    assert assess_memory_quality("ฉันมีแมวชื่ออีอ้วน").importance == 90
    assert assess_memory_quality("ผมมีนกชื่อโมจิ").importance == 90


def test_study_project_importance():
    assert assess_memory_quality("ฉันกำลังเรียนภาษาจีน").importance == 80
    assert assess_memory_quality("ฉันกำลังทำโปรเจกต์ไออีก").importance == 80


def test_rejection_cases():
    assert not assess_memory_quality("ฉันชอบอะไรเกี่ยวกับหลุมดำ").should_store
    assert not assess_memory_quality("หลุมดำคืออะไร").should_store
    assert not assess_memory_quality("ตอนนี้กี่โมง").should_store
    assert not assess_memory_quality("คุยเล่นหน่อย").should_store
