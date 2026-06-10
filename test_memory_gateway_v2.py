from memory_gateway_v2 import save_message_memory_v2

rejected = save_message_memory_v2(
    user_id="demo_user",
    message="หลุมดำคืออะไร",
)

assert rejected["ok"] is True
assert rejected["stored"] is False
assert rejected["reason"] == "memory_quality_rejected"

stored = save_message_memory_v2(
    user_id="demo_user",
    message="ฉันชอบดาวเสาร์",
)

assert stored["ok"] is True
assert stored["stored"] is True
assert stored["backend"] in ("supabase", "local_fallback")
assert stored["record"]["memory_type"] == "user_fact"

print("MEMORY GATEWAY V2 TESTS PASSED")
