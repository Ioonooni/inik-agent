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



def test_main_prompt_uses_persisted_adaptive_personality_as_base_state():
    saved_state = {
        "schema": "adaptive_personality_v1",
        "traits": {
            "warmth": 0.80,
            "playfulness": 0.10,
            "curiosity": 0.20,
            "directness": 0.20,
            "philosophy": 0.20,
            "initiative": 0.10,
            "memory_callback": 0.60,
            "formality": 0.70,
        },
        "metadata": {
            "scope": "per_user",
            "global_identity_mutation": False,
        },
    }

    prompt = build_main_prompt(
        stage_description="Stage: Observer",
        relationship_description="- Trust: 0\n- Familiarity: 0\n- Curiosity: 0",
        user_profile_description="- Recent Mood: neutral\n- Conversation Style: unknown\n- Total Visits: 0",
        response_mode_description="Response Mode: normal_chat",
        chat_history="",
        user_facts={},
        rag_context="ไม่มี RAG memory ที่เกี่ยวข้อง",
        user_message="สวัสดี",
        relationship_state={
            "trust": 0,
            "familiarity": 0,
            "curiosity": 0,
            "attachment": 0,
            "relationship_stage": "Observer",
        },
        adaptive_personality_state=saved_state,
    )

    assert "- warmth: 0.80" in prompt
    assert "- playfulness: 0.10" in prompt
    assert "- memory_callback: 0.60" in prompt
    assert "- formality: 0.70" in prompt


def test_prompt_personalizes_for_explorer_archetype():
    prompt = build_main_prompt(
        stage_description="Stage: Gremlin",
        relationship_description="- Trust: 60\n- Familiarity: 60\n- Curiosity: 80",
        user_profile_description=(
            "- Recent Mood: neutral\n"
            "- Conversation Style: philosophical\n"
            "- User Archetype: explorer\n"
            "- Recurring Topics: ['universe', 'identity']\n"
            "- Topic Affinity: {'universe': 80, 'identity': 60}\n"
            "- Top Topics: ['universe', 'identity']\n"
            "- Recent Memorable Events: []\n"
            "- Total Visits: 8"
        ),
        response_mode_description="Response Mode: normal_chat",
        chat_history="",
        user_facts={},
        rag_context="ไม่มี RAG memory ที่เกี่ยวข้อง",
        user_message="ชีวิตกับจักรวาลมันเกี่ยวกันยังไง",
        relationship_state={
            "trust": 60,
            "familiarity": 60,
            "curiosity": 80,
            "attachment": 40,
            "relationship_score": 60,
            "relationship_stage": "Gremlin",
        },
    )

    assert "User Archetype explorer" in prompt
    assert "จักรวาล" in prompt
    assert "ตัวตน" in prompt
    assert "Topic Affinity Signal" in prompt


def test_prompt_personalizes_for_strategic_builder_archetype():
    prompt = build_main_prompt(
        stage_description="Stage: Observer",
        relationship_description="- Trust: 20\n- Familiarity: 20\n- Curiosity: 40",
        user_profile_description=(
            "- Recent Mood: neutral\n"
            "- Conversation Style: casual\n"
            "- User Archetype: strategic_builder\n"
            "- Recurring Topics: ['business', 'investment', 'technology']\n"
            "- Topic Affinity: {'business': 70, 'investment': 60, 'technology': 50}\n"
            "- Top Topics: ['business', 'investment', 'technology']\n"
            "- Recent Memorable Events: []\n"
            "- Total Visits: 4"
        ),
        response_mode_description="Response Mode: normal_chat",
        chat_history="",
        user_facts={},
        rag_context="ไม่มี RAG memory ที่เกี่ยวข้อง",
        user_message="ควรเริ่มโปรเจกต์นี้ยังไงดี",
        relationship_state={
            "trust": 20,
            "familiarity": 20,
            "curiosity": 40,
            "attachment": 10,
            "relationship_score": 25,
            "relationship_stage": "Observer",
        },
    )

    assert "User Archetype strategic_builder" in prompt
    assert "tradeoffs" in prompt
    assert "ความเสี่ยง" in prompt
    assert "ขั้นตอนที่ทำได้จริง" in prompt


def test_treasure_with_recurring_topics_enables_continuity_and_inside_joke_rules():
    prompt = build_main_prompt(
        stage_description="Stage: Treasure",
        relationship_description="- Trust: 90\n- Familiarity: 90\n- Curiosity: 80",
        user_profile_description=(
            "- Recent Mood: happy\n"
            "- Conversation Style: playful\n"
            "- User Archetype: playful_gremlin\n"
            "- Recurring Topics: ['universe', 'reward', 'play']\n"
            "- Topic Affinity: {'universe': 90, 'play': 80}\n"
            "- Top Topics: ['universe', 'play']\n"
            "- Recent Memorable Events: ['เคยคุยเรื่องดาวเสาร์กับขนม']\n"
            "- Total Visits: 20"
        ),
        response_mode_description="Response Mode: normal_chat",
        chat_history="",
        user_facts={},
        rag_context="ไม่มี RAG memory ที่เกี่ยวข้อง",
        user_message="กลับมาคุยเรื่องดาวอีกแล้ว",
        relationship_state={
            "trust": 90,
            "familiarity": 90,
            "curiosity": 80,
            "attachment": 80,
            "relationship_score": 86,
            "relationship_stage": "Treasure",
        },
    )

    assert "Treasure: อบอุ่นและจำบริบทได้มากขึ้น" in prompt
    assert "Shared Context" in prompt
    assert "Inside Joke V1" in prompt
    assert "continuity" in prompt
    assert "ห้ามสร้างมุกวงในจากเรื่องที่ผู้ใช้ไม่เคยพูด" in prompt
