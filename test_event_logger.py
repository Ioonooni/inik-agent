from event_logger import build_base_event, send_event_to_n8n


class FakeSession(dict):
    pass


def test_build_base_event():
    session = FakeSession(
        user_id="demo_user",
        username="test_user",
        intimacy_score=10,
        points=20,
        current_response_mode="normal_chat",
        relationship_state={
            "trust": 3,
            "familiarity": 4,
            "curiosity": 5,
        },
        user_profile={
            "recent_mood": "neutral",
            "conversation_style": "direct",
            "recurring_topics": ["memory"],
            "total_messages": 7,
            "total_visits": 2,
            "last_interaction_date": "2026-06-12",
        },
        user_facts={"likes": "Saturn"},
        inventory=["เศษดาวสีฟ้า"],
    )

    payload = build_base_event(
        "manual_event_test",
        session,
        extra={"source": "test"},
    )

    assert payload["event_type"] == "manual_event_test"
    assert payload["user_id"] == "demo_user"
    assert payload["username"] == "test_user"
    assert payload["state"]["intimacy_score"] == 10
    assert payload["state"]["points"] == 20
    assert payload["state"]["relationship_state"]["trust"] == 3
    assert payload["state"]["memory_fact_count"] == 1
    assert payload["state"]["inventory_count"] == 1
    assert payload["extra"]["source"] == "test"


if __name__ == "__main__":
    test_build_base_event()
    print("EVENT LOGGER TESTS PASSED")


def test_build_base_event_includes_crm_contract():
    session = FakeSession(
        user_id="u_crm",
        username="crm_user",
        intimacy_score=40,
        points=25,
        current_response_mode="normal_chat",
        relationship_state={
            "trust": 80,
            "familiarity": 80,
            "curiosity": 70,
            "attachment": 60,
            "relationship_score": 78,
            "relationship_stage": "Treasure",
        },
        user_profile={
            "recent_mood": "neutral",
            "conversation_style": "strategic",
            "recurring_topics": ["business"],
            "total_messages": 55,
            "total_visits": 12,
            "last_interaction_date": "2026-06-18",
        },
        user_facts={"likes": "systems", "name": "ไออุ่น", "project": "i nik"},
        inventory=["blue_star_fragment", "mint_cookie", "nebula_token"],
    )

    payload = build_base_event(
        "crm_contract_test",
        session,
        extra={"source": "test"},
    )

    assert payload["crm"]["customer_id"] == "u_crm"
    assert payload["crm"]["username"] == "crm_user"
    assert payload["crm"]["lifecycle_stage"] == "loyal_user"
    assert payload["crm"]["segment"] == "high_relationship"
    assert payload["crm"]["engagement"]["total_messages"] == 55
    assert payload["crm"]["engagement"]["total_visits"] == 12
    assert payload["crm"]["engagement"]["relationship_stage"] == "Treasure"
