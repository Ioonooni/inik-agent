from rick_prompt import build_rick_prompt


def test_rick_prompt_contains_v3_strategic_framework():
    prompt = build_rick_prompt(
        user_profile_description="- User Archetype: strategic_builder",
        chat_history="User: ควรลาออกไหม",
        user_facts={"name": "ไออุ่น", "_internal": "hidden"},
        user_message="ฉันควรลาออกไปทำ startup ไหม",
        rag_context="Relevant memory: ผู้ใช้กำลังทำโปรเจกต์ i nik",
    )

    required = [
        "Rick Royce",
        "strategic reasoning layer",
        "Objective",
        "Tradeoffs",
        "Opportunity cost",
        "Failure mode",
        "Reversibility",
        "Best next action",
        "ข้อเท็จจริง / สมมติฐาน / การตัดสินเชิงกลยุทธ์",
        "ไม่ใช่คำสั่งซื้อขาย",
        "ไออุ่น",
        "ผู้ใช้กำลังทำโปรเจกต์ i nik",
    ]

    for text in required:
        assert text in prompt

    assert "_internal" not in prompt
    assert "motivational coach" in prompt
    assert "trading signal generator" in prompt
