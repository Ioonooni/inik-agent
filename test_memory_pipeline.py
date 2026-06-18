from memory_pipeline import build_memory_from_message, explain_memory_decision

stored = build_memory_from_message(
    user_id="demo_user",
    message="ฉันชอบดาวเสาร์",
)

assert stored is not None
assert stored["memory_type"] == "user_fact"
assert stored["importance"] == 85
assert stored["schema_version"] == "memory_v2"
assert stored["metadata"]["promote_to_long_term"] is True

not_stored = build_memory_from_message(
    user_id="demo_user",
    message="หลุมดำคืออะไร",
)

assert not_stored is None

not_stored_2 = build_memory_from_message(
    user_id="demo_user",
    message="ฉันชอบอะไรเกี่ยวกับหลุมดำ",
)

assert not_stored_2 is None

emotional = build_memory_from_message(
    user_id="demo_user",
    message="วันนี้เหนื่อยมาก",
)

assert emotional is not None
assert emotional["memory_type"] == "emotional_event"
assert emotional["importance"] == 60
assert emotional["metadata"]["promote_to_long_term"] is False

decision = explain_memory_decision("ตอนนี้กี่โมง")
assert decision["should_store"] is False

print("MEMORY PIPELINE TESTS PASSED")
