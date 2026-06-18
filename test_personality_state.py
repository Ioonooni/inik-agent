from personality_state import (
    create_personality_state,
    normalize_personality_state,
    describe_personality_state,
)


def test_default_personality_state_is_per_user_and_bounded():
    state = create_personality_state()

    assert state["schema"] == "adaptive_personality_v1"
    assert state["metadata"]["scope"] == "per_user"
    assert state["metadata"]["global_identity_mutation"] is False

    assert state["traits"]["warmth"] == 0.50
    assert state["traits"]["playfulness"] == 0.45
    assert state["traits"]["initiative"] == 0.25


def test_normalize_clamps_traits_and_blocks_global_mutation():
    state = normalize_personality_state({
        "traits": {
            "warmth": 99,
            "playfulness": -99,
            "initiative": 9,
        },
        "metadata": {
            "scope": "global",
            "global_identity_mutation": True,
            "note": "preserved",
        },
    })

    assert state["traits"]["warmth"] == 0.85
    assert state["traits"]["playfulness"] == 0.0
    assert state["traits"]["initiative"] == 0.60
    assert state["metadata"]["scope"] == "per_user"
    assert state["metadata"]["global_identity_mutation"] is False
    assert state["metadata"]["note"] == "preserved"


def test_describe_personality_state_is_stable_text():
    text = describe_personality_state(create_personality_state())

    assert "Adaptive Personality State:" in text
    assert "- Scope: per-user adaptation" in text
    assert "- Global Identity Mutation: false" in text
    assert "- warmth: 0.50" in text
