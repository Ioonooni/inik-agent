from typing import Any, Dict, List

from rag_memory import search_memory_notes, format_memory_context


def build_safe_rag_context(user_id: str, user_message: str, limit: int = 5) -> str:
    try:
        if not user_id:
            return "ไม่มี RAG memory ที่เกี่ยวข้อง"

        query = (user_message or "").strip()

        if not query:
            return "ไม่มี RAG memory ที่เกี่ยวข้อง"

        result = search_memory_notes(
            user_id=user_id,
            query=query,
            limit=limit
        )

        return format_memory_context(result.get("results", []))

    except Exception as error:
        print("[RAG PROMPT ERROR]", error)
        return "ไม่มี RAG memory ที่เกี่ยวข้อง"


def get_raw_memories(user_id: str, user_message: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        if not user_id:
            return []

        query = (user_message or "").strip()

        if not query:
            return []

        result = search_memory_notes(
            user_id=user_id,
            query=query,
            limit=limit
        )

        return result.get("results", [])

    except Exception as error:
        print("[RAG RAW ERROR]", error)
        return []
