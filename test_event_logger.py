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
