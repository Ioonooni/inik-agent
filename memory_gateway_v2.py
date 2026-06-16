from typing import Any, Dict, List, Optional

from memory_pipeline import build_memory_from_message
from memory_store_v2 import upsert_memory_record, search_memories, list_memories
from supabase_memory import get_supabase_client
from supabase_memory_v2 import upsert_supabase_memory, search_supabase_memories, list_supabase_memories


def save_message_memory_v2(
    user_id: str,
    message: str,
    source: str = "chat",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    record = build_memory_from_message(
        user_id=user_id,
        message=message,
        source=source,
        metadata=metadata,
    )

    if record is None:
        return {
            "ok": True,
            "stored": False,
            "reason": "memory_quality_rejected",
        }

    try:
        client = get_supabase_client()
        result = upsert_supabase_memory(client, record)

        return {
            "ok": True,
            "stored": True,
            "backend": "supabase",
            "record": record,
            "result": result,
        }

    except Exception as error:
        local_result = upsert_memory_record(record)

        return {
            "ok": True,
            "stored": True,
            "backend": "local_fallback",
            "record": record,
            "result": local_result,
            "supabase_error": str(error),
        }


def retrieve_memories_v2(
    user_id: str,
    query: str,
    limit: int = 5,
) -> Dict[str, Any]:
    q = (query or "").strip()
    if not user_id or not q:
        return {"ok": False, "results": [], "reason": "missing user_id or query"}

    try:
        client = get_supabase_client()
        results = search_supabase_memories(
            client=client,
            user_id=user_id,
            query=q,
            limit=limit,
        )
        return {"ok": True, "backend": "supabase", "results": results}

    except Exception as error:
        results = search_memories(query=q, user_id=user_id, limit=limit)
        return {
            "ok": True,
            "backend": "local_fallback",
            "results": results,
            "supabase_error": str(error),
        }


def list_recent_memories_v2(
    user_id: str,
    limit: int = 20,
) -> Dict[str, Any]:
    if not user_id:
        return {"ok": False, "results": [], "reason": "missing user_id"}

    try:
        client = get_supabase_client()
        results = list_supabase_memories(
            client=client,
            user_id=user_id,
            limit=limit,
        )
        return {"ok": True, "backend": "supabase", "results": results}

    except Exception as error:
        results = list_memories(user_id=user_id)[:limit]
        return {
            "ok": True,
            "backend": "local_fallback",
            "results": results,
            "supabase_error": str(error),
        }
