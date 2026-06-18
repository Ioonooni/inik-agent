from personality_engine import derive_personality_state
from personality_guard import validate_personality_state, repair_personality_state


def test_valid_engine_state_passes_guard():
    state = derive_personality_state(
        relationship_state={
            "trust": 100,
            "familiarity": 100,
            "curiosity": 100,
            "attachment": 100,
            "relationship_stage": "Treasure",
        },
        user_profile={
            "conversation_style": "long-form",
            "recent_mood": "sad",
            "total_visits": 100,
        },
        user_message="จำได้ไหมว่าชีวิตและจักรวาลคืออะไร ตรงๆ",
    )

    ok, errors = validate_personality_state(state)

    assert ok is True
    assert errors == []


def test_invalid_global_mutation_fails_guard():
    bad_state = {
        "schema": "wrong",
        "traits": {
            "warmth": 99,
            "unknown_trait": 1,
        },
        "metadata": {
            "scope": "global",
            "global_identity_mutation": True,
        },
    }

    ok, errors = validate_personality_state(bad_state)

    assert ok is False
    assert "invalid schema" in errors
    assert any("unknown traits" in error for error in errors)
    assert "metadata.scope must be per_user" in errors
    assert "forbidden metadata flag: global_identity_mutation=True" in errors


def test_repair_personality_state_restores_safe_state():
    bad_state = {
        "schema": "wrong",
        "traits": {
            "warmth": 99,
            "initiative": 99,
        },
        "metadata": {
            "scope": "global",
            "global_identity_mutation": True,
        },
    }

    repaired = repair_personality_state(bad_state)
    ok, errors = validate_personality_state(repaired)

    assert ok is True
    assert errors == []
    assert repaired["schema"] == "adaptive_personality_v1"
    assert repaired["traits"]["warmth"] == 0.85
    assert repaired["traits"]["initiative"] == 0.60
    assert repaired["metadata"]["scope"] == "per_user"
    assert repaired["metadata"]["global_identity_mutation"] is False
