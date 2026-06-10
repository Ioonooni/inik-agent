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
