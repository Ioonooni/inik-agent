from datetime import datetime, timezone

from supabase_memory import get_supabase_client


def normalize_username(username: str) -> str:
    if not username:
        raise ValueError("username is required")

    cleaned = username.strip().lower()

    if len(cleaned) < 2:
        raise ValueError("username must be at least 2 characters")

    return cleaned


def normalize_email(email: str) -> str:
    if not email:
        raise ValueError("email is required")

    cleaned = email.strip().lower()

    if "@" not in cleaned or "." not in cleaned:
        raise ValueError("invalid email")

    return cleaned


def build_username_from_email(email: str) -> str:
    normalized_email = normalize_email(email)
    base = normalized_email.split("@")[0]
    return normalize_username(base)


def get_user_by_username(username: str):
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

    if result.data:
        return result.data[0]

    return None


def get_user_by_id(user_id: str):
    client = get_supabase_client()

    result = (
        client
        .table("i_nik_users")
        .select("*")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )

    if result.data:
        return result.data[0]

    return None


def memory_exists_for_user(user_id: str) -> bool:
    client = get_supabase_client()

    result = (
        client
        .table("i_nik_memory")
        .select("user_id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    return bool(result.data)


def create_blank_memory_for_user(user_id: str):
    client = get_supabase_client()

    if memory_exists_for_user(user_id):
        return True

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
        client.table("i_nik_memory").insert(blank_memory).execute()
        return True
    except Exception as error:
        print(f"[Auth] Could not create blank memory: {error}")
        return False


def upsert_app_user(user_id: str, username: str):
    """
    Keep this compatible with the current i_nik_users schema.
    Do not write email here unless the table has an email column.
    """
    client = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()

    existing = get_user_by_id(user_id)

    if existing:
        try:
            (
                client
                .table("i_nik_users")
                .update({"last_login": now})
                .eq("id", user_id)
                .execute()
            )
        except Exception as error:
            print(f"[Auth] Could not update app user login time: {error}")

        existing["last_login"] = now
        return existing

    payload = {
        "id": user_id,
        "username": username,
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

        if result.data:
            return result.data[0]

    except Exception as error:
        print(f"[Auth] Could not insert app user: {error}")

    return {
        "id": user_id,
        "username": username,
        "created_at": now,
        "last_login": now,
    }


def sign_up_with_email(email: str, password: str):
    client = get_supabase_client()
    normalized_email = normalize_email(email)

    if not password or len(password) < 6:
        raise ValueError("password must be at least 6 characters")

    auth_result = client.auth.sign_up({
        "email": normalized_email,
        "password": password,
    })

    if not auth_result.user:
        raise RuntimeError("Supabase Auth signup failed")

    user_id = auth_result.user.id
    username = build_username_from_email(normalized_email)

    app_user = upsert_app_user(
        user_id=user_id,
        username=username
    )

    create_blank_memory_for_user(user_id)

    return {
        "id": user_id,
        "username": username,
        "email": normalized_email,
        "auth_user": auth_result.user,
        "session": auth_result.session,
        "app_user": app_user,
    }


def login_with_email(email: str, password: str):
    client = get_supabase_client()
    normalized_email = normalize_email(email)

    if not password:
        raise ValueError("password is required")

    auth_result = client.auth.sign_in_with_password({
        "email": normalized_email,
        "password": password,
    })

    if not auth_result.user:
        raise RuntimeError("Supabase Auth login failed")

    user_id = auth_result.user.id
    username = build_username_from_email(normalized_email)

    app_user = upsert_app_user(
        user_id=user_id,
        username=username
    )

    create_blank_memory_for_user(user_id)

    return {
        "id": user_id,
        "username": username,
        "email": normalized_email,
        "auth_user": auth_result.user,
        "session": auth_result.session,
        "app_user": app_user,
    }


def create_user(username: str):
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

        if result.data:
            user = result.data[0]
            create_blank_memory_for_user(user["id"])
            return user

    except Exception as error:
        print(f"[Auth] Demo user insert failed/refetching: {error}")

        existing = get_user_by_username(normalized)

        if existing:
            create_blank_memory_for_user(existing["id"])
            return existing

    raise RuntimeError(f"Could not create or find user: {normalized}")


def login_or_create_user(username: str):
    client = get_supabase_client()
    normalized = normalize_username(username)
    now = datetime.now(timezone.utc).isoformat()

    existing = get_user_by_username(normalized)

    if existing:
        try:
            (
                client
                .table("i_nik_users")
                .update({"last_login": now})
                .eq("id", existing["id"])
                .execute()
            )
            existing["last_login"] = now
        except Exception as error:
            print(f"[Auth] Demo user login update failed: {error}")

        create_blank_memory_for_user(existing["id"])
        return existing

    return create_user(normalized)


if __name__ == "__main__":
    print("auth_manager ready")