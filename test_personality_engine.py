from personality_engine import derive_personality_state


def test_relationship_signals_increase_traits_without_changing_identity():
    state = derive_personality_state(
        relationship_state={
            "trust": 80,
            "familiarity": 80,
            "curiosity": 80,
            "attachment": 70,
            "relationship_stage": "Treasure",
        },
        user_profile={
            "conversation_style": "long-form",
            "recent_mood": "neutral",
            "total_visits": 12,
        },
        user_message="จำได้ไหมว่าฉันชอบคุยเรื่องจักรวาล",
    )

    assert state["metadata"]["scope"] == "per_user"
    assert state["metadata"]["global_identity_mutation"] is False

    assert state["traits"]["warmth"] == 0.65
    assert state["traits"]["playfulness"] == 0.55
    assert state["traits"]["philosophy"] == 0.70
    assert state["traits"]["memory_callback"] == 0.50
    assert state["traits"]["formality"] == 0.30

    assert state["effective_traits"]["philosophy"] == 0.80
    assert state["effective_traits"]["memory_callback"] == 0.60


def test_emotional_message_temporarily_reduces_playfulness():
    state = derive_personality_state(
        relationship_state={"trust": 0, "familiarity": 0},
        user_profile={"recent_mood": "neutral"},
        user_message="วันนี้เหนื่อยมาก ไม่ไหว",
    )

    assert state["traits"]["warmth"] == 0.50
    assert state["traits"]["playfulness"] == 0.45
    assert state["effective_traits"]["warmth"] == 0.60
    assert state["effective_traits"]["playfulness"] == 0.35
    assert state["temporary_modifiers"]["warmth"] == 0.10
    assert state["temporary_modifiers"]["playfulness"] == -0.10


def test_direct_command_only_changes_effective_directness():
    state = derive_personality_state(
        user_message="สรุปตรงๆ เอาสั้น ๆ",
    )

    assert state["traits"]["directness"] == 0.45
    assert state["effective_traits"]["directness"] == 0.55
    assert state["temporary_modifiers"]["directness"] == 0.10
