from datetime import datetime, timezone

import requests
import streamlit as st

from supabase_memory import get_supabase_client


EVENT_TABLE_NAME = "i_nik_events"


def get_event_webhook_url():
    """Return n8n webhook URL if configured."""
    try:
        return st.secrets.get("N8N_EVENT_WEBHOOK_URL")
    except Exception:
        return None


def build_base_event(event_type, session_state, extra=None):
    """Build one consistent event payload for Supabase and n8n."""
    if extra is None:
        extra = {}

    relationship_state = session_state.get("relationship_state", {})
    user_profile = session_state.get("user_profile", {})
    user_facts = session_state.get("user_facts", {})
    inventory = session_state.get("inventory", [])

    user_id = (
        session_state.get("user_id")
        or extra.get("user_id")
        or "unknown_user"
    )

    username = (
        session_state.get("username")
        or extra.get("username")
        or "unknown"
    )

    intimacy_score = session_state.get("intimacy_score", 0)
    points = session_state.get("points", 0)
    response_mode = session_state.get("current_response_mode", "normal_chat")

    return {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "username": username,
        "state": {
            "intimacy_score": intimacy_score,
            "points": points,
            "current_response_mode": response_mode,
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
        "extra": extra,
    }


def save_event_to_supabase(payload):
    """Save event log to Supabase as primary event storage."""
    try:
        client = get_supabase_client()

        row = {
            "user_id": payload.get("user_id", "unknown_user"),
            "username": payload.get("username", "unknown"),
            "event_type": payload.get("event_type", "unknown_event"),
            "event_payload": payload,
            "intimacy_score": payload.get("state", {}).get("intimacy_score", 0),
            "points": payload.get("state", {}).get("points", 0),
            "response_mode": payload.get("state", {}).get(
                "current_response_mode",
                "normal_chat"
            ),
        }

        response = (
            client
            .table(EVENT_TABLE_NAME)
            .insert(row)
            .execute()
        )

        return {
            "ok": bool(response.data),
            "error": None if response.data else "No event row returned from Supabase"
        }

    except Exception as error:
        return {
            "ok": False,
            "error": str(error)
        }


def send_event_to_n8n(event_type, session_state, extra=None):
    """
    Main event logger.

    Primary:
    - Save event to Supabase.

    Optional:
    - Also send event to n8n if N8N_EVENT_WEBHOOK_URL exists.
    """
    payload = build_base_event(
        event_type,
        session_state,
        extra=extra
    )

    supabase_result = save_event_to_supabase(payload)

    webhook_url = get_event_webhook_url()

    if not webhook_url:
        return {
            "ok": supabase_result["ok"],
            "status_code": None,
            "error": supabase_result["error"],
            "supabase_ok": supabase_result["ok"],
            "n8n_ok": False,
            "n8n_error": "Missing N8N_EVENT_WEBHOOK_URL"
        }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=8
        )

        n8n_ok = response.status_code < 400

        return {
            "ok": supabase_result["ok"] and n8n_ok,
            "status_code": response.status_code,
            "error": None if supabase_result["ok"] and n8n_ok else (
                supabase_result["error"] or response.text
            ),
            "supabase_ok": supabase_result["ok"],
            "n8n_ok": n8n_ok,
            "n8n_error": None if n8n_ok else response.text
        }

    except Exception as error:
        return {
            "ok": supabase_result["ok"],
            "status_code": None,
            "error": supabase_result["error"],
            "supabase_ok": supabase_result["ok"],
            "n8n_ok": False,
            "n8n_error": str(error)
        }