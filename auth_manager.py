from datetime import datetime, timezone
from supabase_memory import get_supabase_client


def normalize_username(username: str) -> str:
    """Normalize username so each typed name maps to one stable user."""
    if not username:
        raise ValueError("username is required")

    cleaned = username.strip().lower()

    if len(cleaned) < 2:
        raise ValueError("username must be at least 2 characters")

    return cleaned


def get_user_by_username(username: str):
    """Return exact user by username, or None if not found."""
    client = get_supabase_client()
    normalized = normalize_username(username)

    result = (
        client
        .table("i_nik_users")
        .select("*")
        .eq("username", normalized)
        .limit(1)
        .execute()
    )

    if result.data and len(result.data) > 0:
        return result.data[0]

    return None


def create_blank_memory_for_user(user_id: str):
    """Ensure every new user gets isolated blank memory."""
    client = get_supabase_client()

    blank_memory = {
        "user_id": user_id,
        "user_facts": {},
        "user_profile": {
            "recent_mood": "neutral",
            "conversation_style": "unknown",
            "recurring_topics": [],
            "memorable_events": [],
            "total_messages": 0,
            "total_visits": 0,
            "last_interaction_date": None,
        },
        "inventory": [],
        "relationship_state": {
            "trust": 0,
            "familiarity": 0,
            "curiosity": 0,
        },
        "intimacy_score": 0,
        "points": 0,
        "current_response_mode": "normal_chat",
    }

    try:
        client.table("i_nik_memory").upsert(blank_memory).execute()
    except Exception as e:
        print(f"[Auth] Could not create blank memory: {e}")


def create_user(username: str):
    """Create a new user and return the exact inserted user."""
    client = get_supabase_client()
    normalized = normalize_username(username)
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "username": normalized,
        "created_at": now,
        "last_login": now,
    }

    try:
        result = (
            client
            .table("i_nik_users")
            .insert(payload)
            .execute()
        )

        if result.data and len(result.data) > 0:
            user = result.data[0]
            create_blank_memory_for_user(user["id"])
            return user

    except Exception as e:
        print(f"[Auth] Create user failed, will refetch exact username: {e}")

    existing = get_user_by_username(normalized)

    if existing:
        return existing

    raise RuntimeError(f"Could not create or find user: {normalized}")


def login_or_create_user(username: str):
    """Login exact username. If not found, create a brand-new user."""
    client = get_supabase_client()
    normalized = normalize_username(username)

    existing = get_user_by_username(normalized)

    if existing:
        now = datetime.now(timezone.utc).isoformat()

        try:
            (
                client
                .table("i_nik_users")
                .update({"last_login": now})
                .eq("id", existing["id"])
                .execute()
            )
            existing["last_login"] = now
        except Exception as e:
            print(f"[Auth] Error updating login time: {e}")

        return existing

    return create_user(normalized)


if __name__ == "__main__":
    test_user = login_or_create_user("test_user")
    print(test_user)