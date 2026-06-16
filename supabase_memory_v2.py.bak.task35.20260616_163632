from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from supabase import Client
except Exception:
    Client = Any


TABLE_NAME = "memories_v2"


def make_memory_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    required = [
        "memory_id",
        "user_id",
        "content",
        "memory_type",
        "importance",
        "source",
        "schema_version",
        "created_at",
        "last_seen_at",
        "hit_count",
        "metadata",
    ]

    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError(f"missing memory fields: {missing}")

    return {key: record[key] for key in required}


def upsert_supabase_memory(
    client: Client,
    record: Dict[str, Any],
    table_name: str = TABLE_NAME,
) -> Dict[str, Any]:
    payload = make_memory_payload(record)

    result = (
        client
        .table(table_name)
        .upsert(payload, on_conflict="memory_id")
        .execute()
    )

    return {
        "ok": True,
        "table": table_name,
        "memory_id": payload["memory_id"],
        "result": result,
    }


def search_supabase_memories(
    client: Client,
    user_id: str,
    query: str,
    table_name: str = TABLE_NAME,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    q = (query or "").strip()

    if not q:
        return []

    result = (
        client
        .table(table_name)
        .select("*")
        .eq("user_id", user_id)
        .ilike("content", f"%{q}%")
        .order("importance", desc=True)
        .limit(limit)
        .execute()
    )

    return list(getattr(result, "data", []) or [])


def list_supabase_memories(
    client: Client,
    user_id: str,
    table_name: str = TABLE_NAME,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    result = (
        client
        .table(table_name)
        .select("*")
        .eq("user_id", user_id)
        .order("last_seen_at", desc=True)
        .limit(limit)
        .execute()
    )

    return list(getattr(result, "data", []) or [])


def mark_supabase_memories_used(
    client: Client,
    memories: List[Dict[str, Any]],
    table_name: str = TABLE_NAME,
) -> Dict[str, Any]:
    updated = 0
    errors = []

    for memory in memories:
        memory_id = memory.get("memory_id")
        if not memory_id:
            continue

        try:
            next_hit_count = int(memory.get("hit_count", 0)) + 1

            client.table(table_name).update({
                "hit_count": next_hit_count,
                "last_seen_at": datetime.now(timezone.utc).isoformat(),
            }).eq("memory_id", memory_id).execute()

            updated += 1

        except Exception as error:
            errors.append(str(error))

    return {
        "ok": len(errors) == 0,
        "updated": updated,
        "errors": errors,
    }
