import json

from relationship import create_relationship_state
from profile import create_user_profile
from memory_gateway import save_memory


def build_memory_snapshot(session_state):
    return {
        "user_facts": session_state.get("user_facts", {}),
        "user_profile": session_state.get("user_profile", create_user_profile()),
        "inventory": session_state.get("inventory", []),
        "intimacy_score": session_state.get("intimacy_score", 0),
        "points": session_state.get("points", 0),
        "relationship_state": session_state.get(
            "relationship_state",
            create_relationship_state()
        ),
        "current_response_mode": session_state.get(
            "current_response_mode",
            "normal_chat"
        )
    }


def export_memory_json(session_state):
    snapshot = build_memory_snapshot(session_state)

    return json.dumps(
        snapshot,
        ensure_ascii=False,
        indent=2
    )


def reset_chat_only(session_state):
    session_state.messages = []


def reset_all_memory(session_state):
    session_state.messages = []
    session_state.user_facts = {}
    session_state.user_profile = create_user_profile()
    session_state.inventory = []
    session_state.intimacy_score = 0
    session_state.points = 0
    session_state.relationship_state = create_relationship_state()
    session_state.current_response_mode = "normal_chat"

    session_state.persistent_memory = {
        "user_facts": session_state.user_facts,
        "user_profile": session_state.user_profile,
        "inventory": session_state.inventory,
        "intimacy_score": session_state.intimacy_score,
        "points": session_state.points,
        "relationship_state": session_state.relationship_state
    }

    save_memory(
        session_state.user_facts,
        session_state.user_profile,
        session_state.inventory,
        session_state.intimacy_score,
        session_state.points,
        session_state.relationship_state
    )

    if "visit_registered" in session_state:
        del session_state["visit_registered"]