from memory_gateway_v2 import save_message_memory_v2
from rag_memory import search_memory_notes
from event_logger import send_event_to_n8n
from redemption import buy_reward_item, redeem_first_inventory_item
from relationship import create_relationship_state, update_relationship_state


class FakeSession(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


def test_memory():
    user_id = "demo_user"
    result = save_message_memory_v2(
        user_id=user_id,
        message="ฉันชอบดาวพฤหัส",
        source="smoke_test",
    )
    assert result.get("stored") is True
    assert result.get("backend") == "supabase"

    found = search_memory_notes(
        user_id=user_id,
        query="ดาวพฤหัส",
        limit=5,
    )
    assert found.get("ok") is True
    assert found.get("backend") == "memories_v2"
    assert len(found.get("results", [])) >= 1


def test_relationship():
    state = create_relationship_state()
    updated = update_relationship_state(
        "วันนี้ฉันรู้สึกเหนื่อยและอยากเล่าเรื่องชีวิต",
        state,
    )
    assert updated["trust"] > 0
    assert updated["familiarity"] > 0
    assert updated["curiosity"] > 0
    assert updated["attachment"] > 0
    assert updated["relationship_score"] > 0
    assert updated["relationship_stage"] in ["Observer", "Gremlin", "Treasure"]


def test_reward_redemption():
    session = FakeSession(
        user_id="demo_user",
        points=20,
        inventory=[],
        user_profile={},
    )

    purchase = buy_reward_item(session, "blue_star_fragment")
    assert purchase["ok"] is True
    assert session.points == 15
    assert len(session.inventory) == 1

    redeemed = redeem_first_inventory_item(session)
    assert redeemed["ok"] is True
    assert "effect_message" in redeemed["record"]


def test_event():
    session = {
        "user_id": "demo_user",
        "username": "smoke_test",
        "intimacy_score": 1,
        "points": 1,
        "relationship_state": {"trust": 1, "familiarity": 1, "curiosity": 1},
        "user_profile": {},
        "user_facts": {},
        "inventory": [],
    }

    result = send_event_to_n8n(
        "smoke_test_event",
        session,
        extra={"source": "smoke_test"},
    )
    assert result.get("supabase_ok") is True


if __name__ == "__main__":
    test_memory()
    test_relationship()
    test_reward_redemption()
    test_event()
    print("SMOKE TEST PASSED")
