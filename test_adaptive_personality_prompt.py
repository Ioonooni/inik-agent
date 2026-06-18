from prompt_builder import build_main_prompt


def test_main_prompt_includes_adaptive_personality_v1():
    prompt = build_main_prompt(
        stage_description="Stage: Gremlin",
        relationship_description="- Trust: 80\n- Familiarity: 80\n- Curiosity: 70",
        user_profile_description="- Recent Mood: neutral\n- Conversation Style: long-form\n- Total Visits: 12",
        response_mode_description="Response Mode: normal_chat",
        chat_history="User: จำเรื่องจักรวาลได้ไหม",
        user_facts={"name": "ไออุ่น", "likes": "จักรวาล"},
        rag_context="ไม่มี RAG memory ที่เกี่ยวข้อง",
        user_message="จำได้ไหมว่าฉันชอบคุยเรื่องจักรวาล",
        relationship_state={
            "trust": 80,
            "familiarity": 80,
            "curiosity": 70,
            "attachment": 60,
            "relationship_stage": "Gremlin",
        },
    )

    assert "กฎ Adaptive Personality V1:" in prompt
    assert "Adaptive Personality V1:" in prompt
    assert "- Scope: per-user adaptation only" in prompt
    assert "- Core identity remains unchanged" in prompt
    assert "- memory_callback:" in prompt
    assert "- philosophy:" in prompt
    assert "ห้ามเปลี่ยน i nik เป็นแฟน therapist customer service หรือ generic assistant" in prompt


def test_adaptive_prompt_responds_to_emotional_context():
    prompt = build_main_prompt(
        stage_description="Stage: Observer",
        relationship_description="- Trust: 0\n- Familiarity: 0\n- Curiosity: 0",
        user_profile_description="- Recent Mood: sad\n- Conversation Style: unknown\n- Total Visits: 0",
        response_mode_description="Response Mode: comfort_choice",
        chat_history="",
        user_facts={},
        rag_context="ไม่มี RAG memory ที่เกี่ยวข้อง",
        user_message="วันนี้เหนื่อยมาก ไม่ไหว",
        relationship_state={
            "trust": 0,
            "familiarity": 0,
            "curiosity": 0,
            "attachment": 0,
            "relationship_stage": "Observer",
        },
    )

    assert "- warmth: 0.60" in prompt
    assert "- playfulness: 0.35" in prompt
    assert "comfort_choice ต้องชนะ personality matrix" in prompt
