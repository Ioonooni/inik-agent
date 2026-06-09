from rag_memory import search_memory_notes, format_memory_context


def build_safe_rag_context(user_id: str, user_message: str, limit: int = 5) -> str:
    try:
        result = search_memory_notes(
            user_id=user_id,
            query=user_message,
            limit=limit
        )

        return format_memory_context(
            result.get("results", [])
        )

    except Exception as error:
        print("[RAG PROMPT ERROR]", error)
        return "ไม่มี RAG memory ที่เกี่ยวข้อง"