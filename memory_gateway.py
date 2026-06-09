from persistent_memory import (
    load_memory as load_memory_from_json,
    save_memory as save_memory_to_json
)
from supabase_memory import (
    get_supabase_client,
    row_to_memory,
    save_memory_to_supabase,
    TABLE_NAME,
    DEMO_USER_ID
)


LAST_MEMORY_STATUS = {
    "source": "unknown",
    "supabase_load": False,
    "supabase_save": False,
    "last_error": None
}


def get_memory_status():
    return LAST_MEMORY_STATUS


def load_memory(user_id=DEMO_USER_ID):
    """
    Main memory loader for i nik V2.

    Priority:
    1. Try Supabase
    2. If no Supabase row exists, migrate local JSON memory to Supabase
    3. If Supabase fails, fallback to JSON
    """

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

        if rows:
            LAST_MEMORY_STATUS["source"] = "supabase"
            LAST_MEMORY_STATUS["supabase_load"] = True
            LAST_MEMORY_STATUS["last_error"] = None
            return row_to_memory(rows[0])

        local_memory = load_memory_from_json()

        migrated = save_memory_to_supabase(
            local_memory["user_facts"],
            local_memory["user_profile"],
            local_memory["inventory"],
            local_memory["intimacy_score"],
            local_memory["points"],
            local_memory["relationship_state"],
            user_id=user_id
        )

        LAST_MEMORY_STATUS["source"] = "json_migrated_to_supabase" if migrated else "json_fallback"
        LAST_MEMORY_STATUS["supabase_load"] = False
        LAST_MEMORY_STATUS["supabase_save"] = migrated

        if not migrated:
            LAST_MEMORY_STATUS["last_error"] = "Supabase row did not exist, and migration save failed."

        return local_memory

    except Exception as error:
        LAST_MEMORY_STATUS["source"] = "json_fallback"
        LAST_MEMORY_STATUS["supabase_load"] = False
        LAST_MEMORY_STATUS["last_error"] = str(error)
        return load_memory_from_json()


def save_memory(
    user_facts,
    user_profile,
    inventory,
    intimacy_score,
    points,
    relationship_state,
    user_id=DEMO_USER_ID
):
    """
    Main memory saver for i nik V2.

    Saves to:
    1. JSON backup
    2. Supabase primary database
    """

    save_memory_to_json(
        user_facts,
        user_profile,
        inventory,
        intimacy_score,
        points,
        relationship_state
    )

    supabase_saved = save_memory_to_supabase(
        user_facts,
        user_profile,
        inventory,
        intimacy_score,
        points,
        relationship_state,
        user_id=user_id
    )

    LAST_MEMORY_STATUS["supabase_save"] = supabase_saved

    if supabase_saved:
        LAST_MEMORY_STATUS["source"] = "supabase_and_json_backup"
        LAST_MEMORY_STATUS["last_error"] = None
    else:
        LAST_MEMORY_STATUS["source"] = "json_backup_only"
        LAST_MEMORY_STATUS["last_error"] = "Supabase save returned False. Check Streamlit secrets, API key type, RLS, or table permissions."

    return supabase_saved