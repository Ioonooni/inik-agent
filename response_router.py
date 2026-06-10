from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from confidence import MemoryConfidence
from memory_verifier import VerifiedMemory, EntryType
from truth_engine import QueryClassification, QueryType


class RouteType:
    STRUCTURED_MEMORY = "STRUCTURED_MEMORY"
    TOOL_ANSWER = "TOOL_ANSWER"
    GEMINI_WITH_CONTEXT = "GEMINI_WITH_CONTEXT"
    GEMINI_NO_MEMORY = "GEMINI_NO_MEMORY"
    FALLBACK = "FALLBACK"


_NO_RAG = "ไม่มี RAG memory ที่เกี่ยวข้อง"

_LIVE_DATA_WARNING = (
    "หมายเหตุสำคัญ: ฉันไม่มีเครื่องมือดูข้อมูลสด เช่น อากาศ ราคา ข่าว หรือเวลาปัจจุบัน "
    "ถ้าถามเรื่องพวกนี้ ให้บอกตรง ๆ ว่าไม่สามารถตรวจสอบได้ "
    "ห้ามตอบสุ่มหรือเดาข้อมูลที่ต้องการเครื่องมือสด"
)


@dataclass
class RouteDecision:
    route_type: str
    direct_reply: Optional[str] = None
    rag_context: str = _NO_RAG
    live_data_warning: Optional[str] = None


def _format_verified_rag(memories: List[VerifiedMemory]) -> str:
    usable = [
        m for m in memories
        if m.confidence in (MemoryConfidence.HIGH, MemoryConfidence.MEDIUM)
        and m.entry_type != EntryType.CONVERSATION_ECHO
    ]

    if not usable:
        return _NO_RAG

    lines = [m.content[:200] for m in usable[:3]]
    quoted = " / ".join(f'"{line}"' for line in lines)
    return f"เธอเคยพูดว่า: {quoted}"


def route(
    classification: QueryClassification,
    user_facts: Dict[str, Any],
    planner_result: Optional[Dict[str, Any]],
    verified_memories: List[VerifiedMemory],
) -> RouteDecision:

    if classification.requires_live_data:
        return RouteDecision(
            route_type=RouteType.GEMINI_NO_MEMORY,
            rag_context=_NO_RAG,
            live_data_warning=_LIVE_DATA_WARNING,
        )

    if classification.query_type == QueryType.TOOL_QUERY:
        if planner_result and planner_result.get("ok"):
            return RouteDecision(
                route_type=RouteType.TOOL_ANSWER,
                rag_context=_NO_RAG,
            )

    if classification.query_type == QueryType.MEMORY_QUERY and classification.can_answer_directly:
        memory_key = classification.memory_key
        value = user_facts.get(memory_key) if memory_key else None

        if value:
            if memory_key == "name":
                direct = f"เธอชื่อ {value} ไง"
            elif memory_key == "likes":
                direct = f"เท่าที่ฉันจำได้ เธอชอบ {value}"
            else:
                direct = f"เท่าที่ฉันจำได้ {memory_key} คือ {value}"

            return RouteDecision(
                route_type=RouteType.STRUCTURED_MEMORY,
                direct_reply=direct,
                rag_context=_NO_RAG,
            )

    if classification.query_type == QueryType.MEMORY_QUERY:
        rag = _format_verified_rag(verified_memories)
        return RouteDecision(
            route_type=RouteType.GEMINI_WITH_CONTEXT,
            rag_context=rag,
        )

    if classification.query_type == QueryType.RELATIONSHIP_QUERY:
        if planner_result and planner_result.get("ok"):
            return RouteDecision(
                route_type=RouteType.TOOL_ANSWER,
                rag_context=_NO_RAG,
            )

    rag = _format_verified_rag(verified_memories)

    if rag != _NO_RAG:
        return RouteDecision(
            route_type=RouteType.GEMINI_WITH_CONTEXT,
            rag_context=rag,
        )

    return RouteDecision(
        route_type=RouteType.GEMINI_NO_MEMORY,
        rag_context=_NO_RAG,
    )
