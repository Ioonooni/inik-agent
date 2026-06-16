from typing import Any, Dict, List

from memory_gateway_v2 import retrieve_memories_v2


NO_RAG_MEMORY = "ไม่มี RAG memory ที่เกี่ยวข้อง"


def _extract_memory_text(memory: Dict[str, Any]) -> str:
    for key in ("text", "content", "message", "summary"):
        value = memory.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    metadata = memory.get("metadata")
    if isinstance(metadata, dict):
        for key in ("text", "content", "message", "summary"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return ""


def _format_memory_context(memories: List[Dict[str, Any]]) -> str:
    if not memories:
        return NO_RAG_MEMORY

    lines = []
    for memory in memories:
        text = _extract_memory_text(memory)
        if not text:
            continue

        memory_type = str(memory.get("memory_type") or "memory")
        rank_score = memory.get("rank_score")

        if isinstance(rank_score, (int, float)):
            label = f"{memory_type} score={rank_score}"
        else:
            label = memory_type

        lines.append(f"- [{label}] {text}")

    if not lines:
        return NO_RAG_MEMORY

    return "Relevant memory:\n" + "\n".join(lines)


def build_safe_rag_context(user_id: str, user_message: str, limit: int = 5) -> str:
    try:
        if not user_id:
            return NO_RAG_MEMORY

        query = (user_message or "").strip()

        if not query:
            return NO_RAG_MEMORY

        result = retrieve_memories_v2(
            user_id=user_id,
            query=query,
            limit=limit,
        )

        return _format_memory_context(result.get("results", []))

    except Exception as error:
        print("[RAG PROMPT ERROR]", error)
        return NO_RAG_MEMORY


def get_raw_memories(user_id: str, user_message: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        if not user_id:
            return []

        query = (user_message or "").strip()

        if not query:
            return []

        result = retrieve_memories_v2(
            user_id=user_id,
            query=query,
            limit=limit,
        )

        return result.get("results", [])

    except Exception as error:
        print("[RAG RAW ERROR]", error)
        return []
