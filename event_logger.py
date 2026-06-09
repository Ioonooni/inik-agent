from datetime import datetime, timezone

import requests
import streamlit as st


def get_event_webhook_url():
    return st.secrets.get("N8N_EVENT_WEBHOOK_URL")


def build_base_event(event_type, session_state, extra=None):
    if extra is None:
        extra = {}

    relationship_state = session_state.get("relationship_state", {})
    user_profile = session_state.get("user_profile", {})
    user_facts = session_state.get("user_facts", {})
    inventory = session_state.get("inventory", [])

    return {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": "demo_user",
        "state": {
            "intimacy_score": session_state.get("intimacy_score", 0),
            "points": session_state.get("points", 0),
            "current_response_mode": session_state.get(
                "current_response_mode",
                "normal_chat"
            ),
            "relationship_state": {
                "trust": relationship_state.get("trust", 0),
                "familiarity": relationship_state.get("familiarity", 0),
                "curiosity": relationship_state.get("curiosity", 0),
            },
            "user_profile": {
                "recent_mood": user_profile.get("recent_mood", "neutral"),
                "conversation_style": user_profile.get(
                    "conversation_style",
                    "unknown"
                ),
                "recurring_topics": user_profile.get("recurring_topics", []),
                "total_messages": user_profile.get("total_messages", 0),
                "total_visits": user_profile.get("total_visits", 0),
                "last_interaction_date": user_profile.get(
                    "last_interaction_date"
                ),
            },
            "memory_fact_count": len(user_facts),
            "inventory_count": len(inventory),
        },
        "extra": extra
    }


def send_event_to_n8n(event_type, session_state, extra=None):
    webhook_url = get_event_webhook_url()

    if not webhook_url:
        return {
            "ok": False,
            "status_code": None,
            "error": "Missing N8N_EVENT_WEBHOOK_URL"
        }

    payload = build_base_event(
        event_type,
        session_state,
        extra=extra
    )

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=8
        )

        return {
            "ok": response.status_code < 400,
            "status_code": response.status_code,
            "error": None if response.status_code < 400 else response.text
        }

    except Exception as error:
        return {
            "ok": False,
            "status_code": None,
            "error": str(error)
        }