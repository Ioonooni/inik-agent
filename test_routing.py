"""
Deterministic routing tests.
Run: python test_routing.py
Exits with code 0 on success, 1 on any failure.
"""
import sys

from truth_engine import classify, QueryType
from memory_verifier import verify, EntryType
from response_router import route, RouteType
from confidence import MemoryConfidence


_PASS = 0
_FAIL = 0


def _check(label: str, condition: bool, detail: str = "") -> None:
    global _PASS, _FAIL
    if condition:
        print(f"  PASS  {label}")
        _PASS += 1
    else:
        print(f"  FAIL  {label}" + (f"  [{detail}]" if detail else ""))
        _FAIL += 1


# ---------------------------------------------------------------------------
# 1. MEMORY_QUERY — must classify correctly
# ---------------------------------------------------------------------------
def test_memory_queries() -> None:
    print("\n=== MEMORY_QUERY (must be MEMORY_QUERY) ===")
    facts = {"name": "ธัญ", "likes": "กาแฟ"}

    cases = [
        "ฉันชื่ออะไร",
        "ฉันชอบอะไร",
        "จำอะไรได้บ้าง",
        "จำได้ไหมว่าฉันชื่ออะไร",
        "ข้อมูลของฉันมีอะไรบ้าง",
        "เราเคยคุยเรื่องอะไร",
        "ฉันเคยบอกอะไรไว้บ้าง",
    ]

    for msg in cases:
        c = classify(msg, facts)
        _check(
            f'"{msg}"',
            c.query_type == QueryType.MEMORY_QUERY,
            f"got {c.query_type}",
        )


# ---------------------------------------------------------------------------
# 2. NOT MEMORY_QUERY — knowledge / factual / normal chat
# ---------------------------------------------------------------------------
def test_not_memory_queries() -> None:
    print("\n=== NOT MEMORY_QUERY (must be FACTUAL_QUERY or NORMAL_CHAT) ===")
    facts = {"name": "ธัญ"}

    cases = [
        "ดาวเสาร์",
        "เล่าเรื่องดาวเสาร์",
        "เล่าเรื่องหลุมดำ",
        "หลุมดำคืออะไร",
        "โลกกลมไหม",
        "2+2 เท่ากับอะไร",
        "อธิบายควอนตัม",
        "เศร้าอะ",
        "เหนื่อย",
        "คุยเล่นหน่อย",
    ]

    for msg in cases:
        c = classify(msg, facts)
        _check(
            f'"{msg}"',
            c.query_type != QueryType.MEMORY_QUERY,
            f"got {c.query_type}",
        )


# ---------------------------------------------------------------------------
# 3. LIVE_DATA_QUERY — must set requires_live_data
# ---------------------------------------------------------------------------
def test_live_data_queries() -> None:
    print("\n=== LIVE_DATA_QUERY (must set requires_live_data=True) ===")

    cases = [
        "วันนี้อากาศเป็นไง",
        "ราคาทองวันนี้เท่าไร",
        "ตอนนี้กี่โมง",
    ]

    for msg in cases:
        c = classify(msg, {})
        _check(
            f'"{msg}"',
            c.requires_live_data is True,
            f"query_type={c.query_type}, requires_live_data={c.requires_live_data}",
        )


# ---------------------------------------------------------------------------
# 4. TOOL_QUERY
# ---------------------------------------------------------------------------
def test_tool_queries() -> None:
    print("\n=== TOOL_QUERY ===")

    cases = [
        "สถานะของฉัน",
        "ฉันมีของรางวัลอะไรบ้าง",
        "คะแนนของฉันเท่าไร",
    ]

    for msg in cases:
        c = classify(msg, {})
        _check(
            f'"{msg}"',
            c.query_type == QueryType.TOOL_QUERY,
            f"got {c.query_type}",
        )


# ---------------------------------------------------------------------------
# 5. Conversation echo must NOT contaminate routing
# ---------------------------------------------------------------------------
def test_echo_does_not_hijack_routing() -> None:
    print("\n=== Echo must NOT hijack routing ===")

    echo_entries = [
        {"content": "เล่าเรื่องหลุมดำ", "memory_type": "conversation_fact"},
        {"content": "ดาวเสาร์", "memory_type": "conversation_fact"},
        {"content": "หลุมดำคืออะไร", "memory_type": "conversation_fact"},
        {"content": "อธิบายควอนตัม", "memory_type": "conversation_fact"},
    ]

    verified = verify(echo_entries)

    # Every entry should be classified as CONVERSATION_ECHO
    for v in verified:
        _check(
            f'stored entry "{v.content}" should be CONVERSATION_ECHO',
            v.entry_type == EntryType.CONVERSATION_ECHO,
            f"got entry_type={v.entry_type}",
        )

    # Full routing for "เล่าเรื่องหลุมดำ": must not be STRUCTURED_MEMORY
    # and must not inject "เธอเคยพูดว่า" echo text
    c = classify("เล่าเรื่องหลุมดำ", {})
    decision = route(
        classification=c,
        user_facts={},
        planner_result=None,
        verified_memories=verified,
    )
    _check(
        '"เล่าเรื่องหลุมดำ" must not route to STRUCTURED_MEMORY',
        decision.route_type != RouteType.STRUCTURED_MEMORY,
        f"got {decision.route_type}",
    )
    _check(
        '"เล่าเรื่องหลุมดำ" must not inject echo as RAG context',
        "เธอเคยพูดว่า" not in decision.rag_context,
        f"rag_context={decision.rag_context}",
    )

    # Factual queries must get GEMINI_NO_MEMORY regardless of echoes
    for msg in ["หลุมดำคืออะไร", "อธิบายควอนตัม", "โลกกลมไหม"]:
        c2 = classify(msg, {})
        d2 = route(
            classification=c2,
            user_facts={},
            planner_result=None,
            verified_memories=verified,
        )
        _check(
            f'"{msg}" must be GEMINI_NO_MEMORY despite echoes in RAG',
            d2.route_type == RouteType.GEMINI_NO_MEMORY,
            f"got {d2.route_type}",
        )


# ---------------------------------------------------------------------------
# 6. STRUCTURED_MEMORY — direct fact answer bypasses Gemini
# ---------------------------------------------------------------------------
def test_structured_memory_direct_answer() -> None:
    print("\n=== STRUCTURED_MEMORY direct answer ===")

    facts = {"name": "ธัญ", "likes": "กาแฟ"}

    c = classify("ฉันชื่ออะไร", facts)
    decision = route(
        classification=c,
        user_facts=facts,
        planner_result=None,
        verified_memories=[],
    )
    _check(
        '"ฉันชื่ออะไร" → STRUCTURED_MEMORY',
        decision.route_type == RouteType.STRUCTURED_MEMORY,
        f"got {decision.route_type}",
    )
    _check(
        "direct_reply contains stored name",
        "ธัญ" in (decision.direct_reply or ""),
        f"got direct_reply={decision.direct_reply}",
    )

    c2 = classify("ฉันชอบอะไร", facts)
    decision2 = route(
        classification=c2,
        user_facts=facts,
        planner_result=None,
        verified_memories=[],
    )
    _check(
        '"ฉันชอบอะไร" → STRUCTURED_MEMORY',
        decision2.route_type == RouteType.STRUCTURED_MEMORY,
        f"got {decision2.route_type}",
    )
    _check(
        "direct_reply contains stored likes",
        "กาแฟ" in (decision2.direct_reply or ""),
        f"got direct_reply={decision2.direct_reply}",
    )


# ---------------------------------------------------------------------------
# 7. Live data warning is injected
# ---------------------------------------------------------------------------
def test_live_data_warning() -> None:
    print("\n=== Live data warning must be set ===")

    for msg in ["วันนี้อากาศเป็นไง", "ราคาทองวันนี้เท่าไร", "ตอนนี้กี่โมง"]:
        c = classify(msg, {})
        decision = route(
            classification=c,
            user_facts={},
            planner_result=None,
            verified_memories=[],
        )
        _check(
            f'"{msg}" live_data_warning must not be None',
            decision.live_data_warning is not None,
            f"got live_data_warning={decision.live_data_warning}",
        )
        _check(
            f'"{msg}" route must be GEMINI_NO_MEMORY',
            decision.route_type == RouteType.GEMINI_NO_MEMORY,
            f"got {decision.route_type}",
        )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_memory_queries()
    test_not_memory_queries()
    test_live_data_queries()
    test_tool_queries()
    test_echo_does_not_hijack_routing()
    test_structured_memory_direct_answer()
    test_live_data_warning()

    print(f"\n{'='*50}")
    print(f"Results: {_PASS} passed, {_FAIL} failed")

    if _FAIL > 0:
        sys.exit(1)

    print("All tests passed.")
    sys.exit(0)
