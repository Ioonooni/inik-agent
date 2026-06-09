from datetime import datetime, timezone

import streamlit as st
from supabase import create_client

from persistent_memory import get_default_memory


TABLE_NAME = "i_nik_memory"
DEMO_USER_ID = "demo_user"


def normalize_supabase_url(url):
    if not url:
        return None

    url = str(url).strip().rstrip("/")

    if "/rest/v1" in url:
        url = url.replace("/rest/v1", "")

    if "/dashboard/" in url:
        raise ValueError(
            "SUPABASE_URL is a dashboard URL. Use the project URL like https://xxxxx.supabase.co"
        )

    return url


def get_redacted_supabase_url():
    url = st.secrets.get("SUPABASE_URL")

    if not url:
        return "SUPABASE_URL missing"

    try:
        normalized_url = normalize_supabase_url(url)
        return normalized_url
    except Exception as error:
        return f"Invalid SUPABASE_URL: {error}"


def get_supabase_client():
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in Streamlit secrets")

    normalized_url = normalize_supabase_url(url)

    return create_client(normalized_url, key)


def row_to_memory(row):
    if not row:
        return get_default_memory()

    memory = get_default_memory()

    memory["user_facts"] = row.get("user_facts") or {}
    memory["user_profile"] = row.get("user_profile") or memory["user_profile"]
    memory["inventory"] = row.get("inventory") or []
    memory["relationship_state"] = (
        row.get("relationship_state")
        or memory["relationship_state"]
    )
    memory["intimacy_score"] = row.get("intimacy_score") or 0
    memory["points"] = row.get("points") or 0

    return memory


def load_memory_from_supabase(user_id=DEMO_USER_ID):
    try:
        client = get_supabase_client()

        response = (
            client.table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if not rows:
            return get_default_memory()

        return row_to_memory(rows[0])

    except Exception as error:
        print(f"[Supabase load fallback] {error}")
        return get_default_memory()


def save_memory_to_supabase(
    user_facts,
    user_profile,
    inventory,
    intimacy_score,
    points,
    relationship_state,
    user_id=DEMO_USER_ID
):
    try:
        client = get_supabase_client()

        payload = {
            "user_id": user_id,
            "user_facts": user_facts,
            "user_profile": user_profile,
            "inventory": inventory,
            "relationship_state": relationship_state,
            "intimacy_score": intimacy_score,
            "points": points,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        client.table(TABLE_NAME).upsert(
            payload,
            on_conflict="user_id"
        ).execute()

        return True

    except Exception as error:
        print(f"[Supabase save failed] {error}")
        return False