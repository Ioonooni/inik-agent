from typing import Any, Dict, List, Optional

from memory_pipeline import build_memory_from_message
from memory_store_v2 import list_memories, upsert_memory_record
from supabase_memory import get_supabase_client
from supabase_memory_v2 import fetch_conflictable_memories, supersede_supabase_memory, upsert_supabase_memory


_CONFLICTABLE_TYPES = {"user_fact", "preference"}


def _check_and_supersede_conflicts(client: Any, record: Dict[str, Any]) -> Dict[str, Any]:
    """Detect same-category conflicts and soft-supersede the losing record. Never raises."""
    try:
        if record.get("memory_type") not in _CONFLICTABLE_TYPES:
            return {"checked": False, "reason": "non_conflictable_type"}

        from memory_schema import detect_memory_conflict, mark_memory_superseded

        existing_memories = fetch_conflictable_memories(client, user_id=record["user_id"])
        superseded_count = 0
        errors: List[str] = []

        for existing in existing_memories:
            if existing.get("memory_id") == record.get("memory_id"):
                continue

            conflict = detect_memory_conflict(existing, record)
            if not conflict["conflict"] or conflict["winner"] != "incoming":
                continue

            superseded = mark_memory_superseded(existing, record)
            try:
                supersede_supabase_memory(
                    client,
                    memory_id=superseded["memory_id"],
                    metadata=superseded["metadata"],
                )
                superseded_count += 1
            except Exception as wb_error:
                errors.append(str(wb_error))

        result: Dict[str, Any] = {"checked": True, "superseded": superseded_count}
        if errors:
            result["writeback_errors"] = errors
        return result

    except Exception as exc:
        return {"checked": False, "error": str(exc)}


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
        conflict_summary = _check_and_supersede_conflicts(client, record)
        result = upsert_supabase_memory(client, record)

        return {
            "ok": True,
            "stored": True,
            "backend": "supabase",
            "record": record,
            "result": result,
            "conflict_summary": conflict_summary,
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
            "conflict_summary": {
                "checked": False,
                "reason": "supabase_unavailable_local_fallback",
            },
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
        try:
            from memory_ranking import rank_memories
            candidates = list_memories(user_id=user_id)
            ranked = rank_memories(candidates, limit=limit, query=query)
            return {
                "ok": True,
                "backend": "local_json_fallback",
                "supabase_error": str(error),
                "results": ranked,
            }
        except Exception:
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
        try:
            from memory_ranking import rank_memories
            candidates = list_memories(user_id=user_id)
            ranked = rank_memories(candidates, limit=limit, query="")
            return {
                "ok": True,
                "backend": "local_json_fallback_recent",
                "supabase_error": str(error),
                "results": ranked,
            }
        except Exception:
            return {
                "ok": False,
                "backend": "memory_gateway_v2_recent_failed",
                "error": str(error),
                "results": [],
            }
