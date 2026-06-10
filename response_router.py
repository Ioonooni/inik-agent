from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from confidence import MemoryConfidence
from memory_verifier import VerifiedMemory, EntryType
from truth_engine import QueryClassification, QueryType


class RouteType:
    DIRECT_ANSWER = "DIRECT_ANSWER"
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


def _format_memory_rag(memories: List[VerifiedMemory]) -> str:
    """For MEMORY_QUERY: include facts, preferences, events; exclude echoes."""
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


def _format_chat_rag(memories: List[VerifiedMemory]) -> str:
    """For NORMAL_CHAT: only genuine user facts and preferences, never echoes or inferences."""
    usable = [
        m for m in memories
        if m.confidence in (MemoryConfidence.HIGH, MemoryConfidence.MEDIUM)
        and m.entry_type in (EntryType.USER_FACT, EntryType.PREFERENCE)
    ]

    if not usable:
        return _NO_RAG

    lines = [m.content[:200] for m in usable[:2]]
    quoted = " / ".join(f'"{line}"' for line in lines)
    return f"เธอเคยพูดว่า: {quoted}"


def route(
    classification: QueryClassification,
    user_facts: Dict[str, Any],
    planner_result: Optional[Dict[str, Any]],
    verified_memories: List[VerifiedMemory],
) -> RouteDecision:

    # Live data — Gemini gets warning, no RAG injection
    if classification.requires_live_data:
        return RouteDecision(
            route_type=RouteType.GEMINI_NO_MEMORY,
            rag_context=_NO_RAG,
            live_data_warning=_LIVE_DATA_WARNING,
        )

    # Factual / knowledge — answer directly if deterministic (e.g. arithmetic), else Gemini
    if classification.query_type == QueryType.FACTUAL_QUERY:
        if classification.can_answer_directly and classification.direct_answer is not None:
            return RouteDecision(
                route_type=RouteType.DIRECT_ANSWER,
                direct_reply=classification.direct_answer,
                rag_context=_NO_RAG,
            )
        return RouteDecision(
            route_type=RouteType.GEMINI_NO_MEMORY,
            rag_context=_NO_RAG,
        )

    # Tool query — answered by planner
    if classification.query_type == QueryType.TOOL_QUERY:
        if planner_result and planner_result.get("ok"):
            return RouteDecision(
                route_type=RouteType.TOOL_ANSWER,
                rag_context=_NO_RAG,
            )

    # Relationship query — answered by planner
    if classification.query_type == QueryType.RELATIONSHIP_QUERY:
        if planner_result and planner_result.get("ok"):
            return RouteDecision(
                route_type=RouteType.TOOL_ANSWER,
                rag_context=_NO_RAG,
            )

    # Explicit memory query with a direct fact available — bypass Gemini
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

    # Explicit memory query without a direct fact — use verified RAG context for Gemini
    if classification.query_type == QueryType.MEMORY_QUERY:
        rag = _format_memory_rag(verified_memories)
        return RouteDecision(
            route_type=RouteType.GEMINI_WITH_CONTEXT,
            rag_context=rag,
        )

    # Normal chat — only inject genuine user facts/preferences as background context
    rag = _format_chat_rag(verified_memories)

    if rag != _NO_RAG:
        return RouteDecision(
            route_type=RouteType.GEMINI_WITH_CONTEXT,
            rag_context=rag,
        )

    return RouteDecision(
        route_type=RouteType.GEMINI_NO_MEMORY,
        rag_context=_NO_RAG,
    )
