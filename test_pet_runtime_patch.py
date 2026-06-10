from memory_direct_answer import answer_direct_memory_recall

facts = []
memories = [
    {"content": "แมวฉันชื่ออีอ้วน"},
    {"content": "ฉันชอบชานม"},
]

tests = [
    "สัตว์เลี้ยงฉันชื่ออะไร",
    "สัตว์เลี้ยงของฉันชื่ออะไร",
    "แมวฉันชื่ออะไร",
]

for q in tests:
    ans = answer_direct_memory_recall(q, facts, memories)
    print(q, "=>", ans)
    assert ans and "อีอ้วน" in ans

print("PET RUNTIME PATCH TESTS PASSED")
