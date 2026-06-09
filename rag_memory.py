from datetime import datetime, timezone
from typing import Any, Dict, List

from supabase_memory import get_supabase_client


TABLE_NAME = "i_nik_rag_memory"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(text: str) -> str:
    if not text:
        return ""

    return text.strip()


def save_memory_note(
    user_id: str,
    content: str,
    memory_type: str = "conversation_fact",
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    client = get_supabase_client()
    cleaned = normalize_text(content)

    if not user_id:
        return {"ok": False, "error": "Missing user_id"}

    if not cleaned:
        return {"ok": False, "error": "Missing content"}

    payload = {
        "user_id": user_id,
        "content": cleaned,
        "memory_type": memory_type,
        "metadata": metadata or {},
        "created_at": now_iso(),
    }

    try:
        result = (
            client
            .table(TABLE_NAME)
            .insert(payload)
            .execute()
        )

        return {
            "ok": True,
            "row": result.data[0] if result.data else payload
        }

    except Exception as error:
        return {
            "ok": False,
            "error": str(error)
        }


def search_memory_notes(
    user_id: str,
    query: str,
    limit: int = 5
) -> Dict[str, Any]:
    client = get_supabase_client()
    cleaned_query = normalize_text(query)

    if not user_id:
        return {"ok": False, "error": "Missing user_id", "results": []}

    if not cleaned_query:
        return {"ok": False, "error": "Missing query", "results": []}

    try:
        result = (
            client
            .table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .ilike("content", f"%{cleaned_query}%")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return {
            "ok": True,
            "results": result.data or []
        }

    except Exception as error:
        return {
            "ok": False,
            "error": str(error),
            "results": []
        }


def list_recent_memory_notes(
    user_id: str,
    limit: int = 10
) -> Dict[str, Any]:
    client = get_supabase_client()

    if not user_id:
        return {"ok": False, "error": "Missing user_id", "results": []}

    try:
        result = (
            client
            .table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return {
            "ok": True,
            "results": result.data or []
        }

    except Exception as error:
        return {
            "ok": False,
            "error": str(error),
            "results": []
        }


def format_memory_context(memories: List[Dict[str, Any]]) -> str:
    if not memories:
        return "ไม่มี RAG memory ที่เกี่ยวข้อง"

    lines = []

    for memory in memories:
        content = memory.get("content", "")
        memory_type = memory.get("memory_type", "memory")
        created_at = memory.get("created_at", "")

        lines.append(f"- [{memory_type}] {content} ({created_at})")

    return "\n".join(lines)


if __name__ == "__main__":
    print("rag_memory v1 ready")