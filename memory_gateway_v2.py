from typing import Any, Dict, Optional

from memory_pipeline import build_memory_from_message
from memory_store_v2 import upsert_memory_record
from supabase_memory import get_supabase_client
from supabase_memory_v2 import upsert_supabase_memory


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
    """Safe retrieval wrapper for shared memory search."""
    try:
        from rag_memory import search_memory_notes

        return search_memory_notes(
            user_id=user_id,
            query=query,
            limit=limit,
        )
    except Exception as error:
        return {
            "ok": False,
            "backend": "memory_gateway_v2_retrieve_failed",
            "error": str(error),
            "results": [],
        }


def list_recent_memories_v2(
    user_id: str,
    limit: int = 10,
) -> Dict[str, Any]:
    """Safe retrieval wrapper for recent shared memories."""
    try:
        from rag_memory import list_recent_memory_notes

        return list_recent_memory_notes(
            user_id=user_id,
            limit=limit,
        )
    except Exception as error:
        return {
            "ok": False,
            "backend": "memory_gateway_v2_recent_failed",
            "error": str(error),
            "results": [],
        }
