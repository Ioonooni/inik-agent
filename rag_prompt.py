from rag_memory import search_memory_notes, list_recent_memory_notes, format_memory_context


QUESTION_KEYWORDS = [
    "อะไร", "เคย", "จำได้ไหม", "จำได้มั้ย", "ชอบอะไร",
    "พูดเรื่อง", "บอกว่า", "เคยบอก"
]


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

        memories = result.get("results", [])

        if not memories and any(word in query for word in QUESTION_KEYWORDS):
            recent_result = list_recent_memory_notes(
                user_id=user_id,
                limit=limit
            )
            memories = recent_result.get("results", [])

        return format_memory_context(memories)

    except Exception as error:
        print("[RAG PROMPT ERROR]", error)
        return "ไม่มี RAG memory ที่เกี่ยวข้อง"