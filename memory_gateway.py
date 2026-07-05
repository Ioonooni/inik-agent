import logging

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

from user_profile import create_user_profile
from relationship import create_relationship_state

_log = logging.getLogger("inik.supabase")


LAST_MEMORY_STATUS = {
    "source": "unknown",
    "supabase_load": False,
    "supabase_save": False,
    "last_error": None
}


def get_memory_status():
    return LAST_MEMORY_STATUS


def create_blank_memory():
    """Create isolated blank memory for a brand-new user."""
    return {
        "user_facts": {},
        "user_profile": create_user_profile(),
        "inventory": [],
        "intimacy_score": 0,
        "points": 0,
        "relationship_state": create_relationship_state()
    }


def load_memory(user_id=DEMO_USER_ID):
    """
    Main memory loader for i nik V2.

    Rule:
    - Existing Supabase row = load that user's memory.
    - New Supabase user with no memory row = create blank isolated memory.
    - JSON is fallback only for demo_user / emergency local fallback.
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

        blank_memory = create_blank_memory()

        created = save_memory_to_supabase(
            blank_memory["user_facts"],
            blank_memory["user_profile"],
            blank_memory["inventory"],
            blank_memory["intimacy_score"],
            blank_memory["points"],
            blank_memory["relationship_state"],
            user_id=user_id
        )

        LAST_MEMORY_STATUS["source"] = "supabase_blank_created" if created else "blank_memory_local_only"
        LAST_MEMORY_STATUS["supabase_load"] = False
        LAST_MEMORY_STATUS["supabase_save"] = created
        LAST_MEMORY_STATUS["last_error"] = None if created else "No Supabase row existed and blank memory save failed."

        return blank_memory

    except Exception as exc:
        _log.warning("[supabase] load failed: %s", type(exc).__name__)
        LAST_MEMORY_STATUS["supabase_load"] = False
        LAST_MEMORY_STATUS["last_error"] = type(exc).__name__

        if user_id == DEMO_USER_ID:
            LAST_MEMORY_STATUS["source"] = "json_fallback_demo_user"
            return load_memory_from_json()

        LAST_MEMORY_STATUS["source"] = "blank_memory_fallback_non_demo_user"
        return create_blank_memory()


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

    Rule:
    - Supabase is primary.
    - JSON backup is written only for demo_user to prevent cross-user leakage.
    """

    if user_id == DEMO_USER_ID:
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
        LAST_MEMORY_STATUS["source"] = "supabase_primary"
        LAST_MEMORY_STATUS["last_error"] = None
    else:
        LAST_MEMORY_STATUS["source"] = "json_demo_backup_only" if user_id == DEMO_USER_ID else "supabase_save_failed_non_demo_user"
        LAST_MEMORY_STATUS["last_error"] = "Supabase save returned False. Check secrets, API key type, RLS, or table permissions."

    return supabase_saved