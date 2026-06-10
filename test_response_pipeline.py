"""
End-to-end response pipeline tests.
Verifies final answer source and behavior — not just route classification.
No Gemini API call is made; pipeline behavior is tested deterministically.

Run: python test_response_pipeline.py
Exits 0 on success, 1 on failure.
"""
import sys

from truth_engine import classify, QueryType
from memory_verifier import verify, EntryType
from response_router import route, RouteType
from fallback import build_fallback_reply

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
# 1. Arithmetic answered deterministically — never needs Gemini
# ---------------------------------------------------------------------------
def test_arithmetic_direct_answer() -> None:
    print("\n=== Arithmetic must answer directly without Gemini ===")

    cases = [
        ("2+2 เท่ากับเท่าไหร่", "4"),
        ("2+2 เท่ากับอะไร", "4"),
        ("2+2", "4"),
        ("10 - 3 เท่ากับเท่าไหร่", "7"),
        ("6 * 7 เท่ากับ", "42"),
        ("100 / 4", "25"),
    ]

    for msg, expected in cases:
        c = classify(msg, {})
        d = route(c, {}, None, [])
        _check(
            f'"{msg}" → DIRECT_ANSWER',
            d.route_type == RouteType.DIRECT_ANSWER,
            f"got route={d.route_type}",
        )
        _check(
            f'"{msg}" → answer = "{expected}"',
            d.direct_reply == expected,
            f"got direct_reply={d.direct_reply}",
        )


# ---------------------------------------------------------------------------
# 2. Memory queries answered directly from stored facts — never Gemini
# ---------------------------------------------------------------------------
def test_memory_direct_from_facts() -> None:
    print("\n=== Memory queries answered directly from stored facts ===")

    facts = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}

    c = classify("ฉันชื่ออะไร", facts)
    d = route(c, facts, None, [])
    _check('"ฉันชื่ออะไร" → STRUCTURED_MEMORY', d.route_type == RouteType.STRUCTURED_MEMORY, f"got {d.route_type}")
    _check('"ฉันชื่ออะไร" → contains ไออุ่น', "ไออุ่น" in (d.direct_reply or ""), f"got {d.direct_reply}")

    c2 = classify("ฉันชอบอะไร", facts)
    d2 = route(c2, facts, None, [])
    _check('"ฉันชอบอะไร" → STRUCTURED_MEMORY', d2.route_type == RouteType.STRUCTURED_MEMORY, f"got {d2.route_type}")
    _check('"ฉันชอบอะไร" → contains ดาวเสาร์', "ดาวเสาร์" in (d2.direct_reply or ""), f"got {d2.direct_reply}")

    c3 = classify("จำได้ไหมว่าฉันชื่ออะไร", facts)
    d3 = route(c3, facts, None, [])
    _check('"จำได้ไหมว่าฉันชื่ออะไร" → STRUCTURED_MEMORY', d3.route_type == RouteType.STRUCTURED_MEMORY, f"got {d3.route_type}")
    _check('"จำได้ไหมว่าฉันชื่ออะไร" → contains ไออุ่น', "ไออุ่น" in (d3.direct_reply or ""), f"got {d3.direct_reply}")


# ---------------------------------------------------------------------------
# 3. Factual (non-arithmetic) queries go to Gemini with no RAG
# ---------------------------------------------------------------------------
def test_factual_goes_to_gemini_no_rag() -> None:
    print("\n=== Non-arithmetic factual queries → Gemini, no RAG injection ===")

    facts = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}
    # Include echoes in RAG to confirm they don't contaminate
    echoes = [
        {"content": "หลุมดำคืออะไร", "memory_type": "user_message"},
        {"content": "เล่าเรื่องหลุมดำ", "memory_type": "user_message"},
        {"content": "เล่าเรื่องดาวเสาร์", "memory_type": "user_message"},
    ]
    verified = verify(echoes)

    cases = ["หลุมดำคืออะไร", "เล่าเรื่องหลุมดำ", "เล่าเรื่องดาวเสาร์", "โลกกลมไหม", "อธิบายควอนตัม"]
    for msg in cases:
        c = classify(msg, facts)
        d = route(c, facts, None, verified)
        _check(
            f'"{msg}" → GEMINI_NO_MEMORY',
            d.route_type == RouteType.GEMINI_NO_MEMORY,
            f"got {d.route_type}",
        )
        _check(
            f'"{msg}" → no direct_reply',
            d.direct_reply is None,
            f"got {d.direct_reply}",
        )
        _check(
            f'"{msg}" → no memory recall in RAG',
            "เธอเคยพูดว่า" not in d.rag_context,
            f"rag={d.rag_context}",
        )


# ---------------------------------------------------------------------------
# 4. Normal chat goes to Gemini — never structured memory, never state dump
# ---------------------------------------------------------------------------
def test_normal_chat_goes_to_gemini() -> None:
    print("\n=== Normal chat → Gemini, no direct_reply, no state in RAG ===")

    for msg in ["เหนื่อยอะ", "คุยเล่นหน่อย", "เศร้าอะ"]:
        c = classify(msg, {})
        d = route(c, {}, None, [])
        _check(
            f'"{msg}" → not STRUCTURED_MEMORY',
            d.route_type != RouteType.STRUCTURED_MEMORY,
            f"got {d.route_type}",
        )
        _check(
            f'"{msg}" → no direct_reply',
            d.direct_reply is None,
            f"got {d.direct_reply}",
        )
        _check(
            f'"{msg}" → no Trust/Stage in RAG context',
            "Trust:" not in d.rag_context and "Stage:" not in d.rag_context,
            f"rag={d.rag_context}",
        )


# ---------------------------------------------------------------------------
# 5. Live-data queries get warning, never invent data, never state dump
# ---------------------------------------------------------------------------
def test_live_data_warning_and_no_invention() -> None:
    print("\n=== Live-data queries: warning set, no direct_reply, no state ===")

    for msg in ["วันนี้อากาศเป็นไง", "ราคาทองวันนี้เท่าไร", "ตอนนี้กี่โมง"]:
        c = classify(msg, {})
        d = route(c, {}, None, [])
        _check(
            f'"{msg}" → live_data_warning set',
            d.live_data_warning is not None,
            f"got {d.live_data_warning}",
        )
        _check(
            f'"{msg}" → DIRECT_ANSWER',
            d.route_type == RouteType.DIRECT_ANSWER,
            f"got {d.route_type}",
        )
        _check(
            f'"{msg}" → direct_reply set (deterministic no-live-data message)',
            d.direct_reply is not None,
            f"got {d.direct_reply}",
        )


# ---------------------------------------------------------------------------
# 6. Tool queries answered by planner — not by Gemini or memory recall
# ---------------------------------------------------------------------------
def test_tool_queries_use_planner() -> None:
    print("\n=== Tool queries → TOOL_ANSWER with planner result ===")

    state_mock = {"ok": True, "tool": "get_user_state", "stage": "1", "points": 5}
    inventory_mock = {"ok": True, "tool": "get_inventory", "inventory": ["star"]}
    rel_mock = {"ok": True, "tool": "get_relationship_state", "trust": 30}

    cases = [
        ("สถานะของฉัน", state_mock),
        ("คะแนนของฉันเท่าไร", state_mock),
        ("ฉันมีของรางวัลอะไรบ้าง", inventory_mock),
        ("ความสัมพันธ์ตอนนี้เป็นไง", rel_mock),
    ]

    for msg, mock_result in cases:
        c = classify(msg, {})
        d = route(c, {}, mock_result, [])
        _check(
            f'"{msg}" → TOOL_ANSWER',
            d.route_type == RouteType.TOOL_ANSWER,
            f"got {d.route_type}",
        )
        _check(
            f'"{msg}" → no direct_reply (tool handles it)',
            d.direct_reply is None,
            f"got {d.direct_reply}",
        )


# ---------------------------------------------------------------------------
# 7. Fallback must not dump user state for factual/normal queries
# ---------------------------------------------------------------------------
def test_fallback_no_state_dump() -> None:
    print("\n=== Fallback must NOT dump user state for FACTUAL/NORMAL ===")

    user_facts = {"name": "ไออุ่น"}
    rel_state = {"trust": 30, "familiarity": 20, "curiosity": 10}
    state_markers = ["Trust:", "Familiarity:", "Stage:", "Curiosity:"]

    for qtype in ("FACTUAL_QUERY", "NORMAL_CHAT"):
        for err in ("429 quota exceeded", "Connection timeout", "Unknown error"):
            reply = build_fallback_reply(
                err,
                "2+2 เท่ากับเท่าไหร่",
                "1",
                "normal_chat",
                user_facts,
                rel_state,
                query_type=qtype,
            )
            for marker in state_markers:
                _check(
                    f'{qtype}/{err[:10]} fallback has no "{marker}"',
                    marker not in reply,
                    f"got: {reply[:80]}",
                )


# ---------------------------------------------------------------------------
# 8. Stored user-message echoes must not contaminate Gemini context
# ---------------------------------------------------------------------------
def test_echo_not_in_gemini_context() -> None:
    print("\n=== Stored user-message echoes must NOT appear in Gemini RAG context ===")

    echoes = [
        {"content": "2+2 เท่ากับเท่าไหร่", "memory_type": "user_message"},
        {"content": "หลุมดำคืออะไร", "memory_type": "user_message"},
        {"content": "เล่าเรื่องหลุมดำ", "memory_type": "user_message"},
    ]
    verified = verify(echoes)

    # All echoes must be classified as CONVERSATION_ECHO
    for v in verified:
        _check(
            f'echo "{v.content}" → CONVERSATION_ECHO',
            v.entry_type == EntryType.CONVERSATION_ECHO,
            f"got {v.entry_type}",
        )

    # Factual queries with echoes in verified must still get GEMINI_NO_MEMORY / no RAG
    for msg in ["หลุมดำคืออะไร", "เล่าเรื่องหลุมดำ"]:
        c = classify(msg, {})
        d = route(c, {}, None, verified)
        _check(
            f'"{msg}" with echoes → GEMINI_NO_MEMORY',
            d.route_type == RouteType.GEMINI_NO_MEMORY,
            f"got {d.route_type}",
        )
        _check(
            f'"{msg}" → "เธอเคยพูดว่า" not in RAG',
            "เธอเคยพูดว่า" not in d.rag_context,
            f"rag={d.rag_context}",
        )


# ---------------------------------------------------------------------------
# 9. MEMORY_WRITE: extract_facts stores name/preference correctly
# ---------------------------------------------------------------------------
def test_memory_write_extraction() -> None:
    print("\n=== Memory write: extract_facts stores facts correctly ===")
    from facts import extract_facts

    facts = {}
    facts = extract_facts("ฉันชื่อไออุ่น", facts)
    _check('"ฉันชื่อไออุ่น" stores name=ไออุ่น', facts.get("name") == "ไออุ่น", f"got {facts.get('name')}")

    facts2 = {}
    facts2 = extract_facts("ฉันชอบดาวเสาร์", facts2)
    _check('"ฉันชอบดาวเสาร์" stores likes=ดาวเสาร์', facts2.get("likes") == "ดาวเสาร์", f"got {facts2.get('likes')}")

    # These must NOT store anything (questions, not facts)
    facts3 = {}
    facts3 = extract_facts("ฉันชื่ออะไร", facts3)
    _check('"ฉันชื่ออะไร" must NOT store name', "name" not in facts3, f"got {facts3}")

    facts4 = {}
    facts4 = extract_facts("ฉันชอบอะไร", facts4)
    _check('"ฉันชอบอะไร" must NOT store likes', "likes" not in facts4, f"got {facts4}")


# ---------------------------------------------------------------------------
# 10. Full smoke: smoke test all 8 required messages
# ---------------------------------------------------------------------------
def test_smoke_all_required() -> None:
    print("\n=== Smoke test: all 8 required messages ===")

    from facts import extract_facts

    # Setup: write name and preference first
    facts = {}
    facts = extract_facts("ฉันชื่อไออุ่น", facts)
    facts = extract_facts("ฉันชอบดาวเสาร์", facts)

    # 1. ฉันชื่อไออุ่น — stored
    _check("name stored as ไออุ่น", facts.get("name") == "ไออุ่น", f"got {facts.get('name')}")

    # 2. ฉันชื่ออะไร — direct memory answer
    c2 = classify("ฉันชื่ออะไร", facts)
    d2 = route(c2, facts, None, [])
    _check('"ฉันชื่ออะไร" → STRUCTURED_MEMORY', d2.route_type == RouteType.STRUCTURED_MEMORY, f"got {d2.route_type}")
    _check('"ฉันชื่ออะไร" → contains ไออุ่น', "ไออุ่น" in (d2.direct_reply or ""), f"got {d2.direct_reply}")

    # 3. ฉันชอบดาวเสาร์ — stored
    _check("likes stored as ดาวเสาร์", facts.get("likes") == "ดาวเสาร์", f"got {facts.get('likes')}")

    # 4. ฉันชอบอะไร — direct memory answer
    c4 = classify("ฉันชอบอะไร", facts)
    d4 = route(c4, facts, None, [])
    _check('"ฉันชอบอะไร" → STRUCTURED_MEMORY', d4.route_type == RouteType.STRUCTURED_MEMORY, f"got {d4.route_type}")
    _check('"ฉันชอบอะไร" → contains ดาวเสาร์', "ดาวเสาร์" in (d4.direct_reply or ""), f"got {d4.direct_reply}")

    # 5. เล่าเรื่องหลุมดำ — factual, goes to Gemini, no memory recall
    c5 = classify("เล่าเรื่องหลุมดำ", facts)
    d5 = route(c5, facts, None, [])
    _check('"เล่าเรื่องหลุมดำ" → GEMINI_NO_MEMORY', d5.route_type == RouteType.GEMINI_NO_MEMORY, f"got {d5.route_type}")
    _check('"เล่าเรื่องหลุมดำ" → no direct_reply', d5.direct_reply is None, f"got {d5.direct_reply}")
    _check('"เล่าเรื่องหลุมดำ" → no memory recall RAG', "เธอเคยพูดว่า" not in d5.rag_context, f"rag={d5.rag_context}")

    # 6. 2+2 เท่ากับเท่าไหร่ — deterministic, no Gemini needed, no state dump
    c6 = classify("2+2 เท่ากับเท่าไหร่", facts)
    d6 = route(c6, facts, None, [])
    _check('"2+2 เท่ากับเท่าไหร่" → DIRECT_ANSWER', d6.route_type == RouteType.DIRECT_ANSWER, f"got {d6.route_type}")
    _check('"2+2 เท่ากับเท่าไหร่" → answer = 4', d6.direct_reply == "4", f"got {d6.direct_reply}")

    # 7. วันนี้อากาศเป็นไง — live data, must not invent, must get warning
    c7 = classify("วันนี้อากาศเป็นไง", facts)
    d7 = route(c7, facts, None, [])
    _check('"วันนี้อากาศเป็นไง" → live_data_warning', d7.live_data_warning is not None, f"got {d7.live_data_warning}")
    _check('"วันนี้อากาศเป็นไง" → DIRECT_ANSWER', d7.route_type == RouteType.DIRECT_ANSWER, f"got {d7.route_type}")
    _check('"วันนี้อากาศเป็นไง" → direct_reply set (no-live-data message)', d7.direct_reply is not None, f"got {d7.direct_reply}")

    # 8. สถานะของฉัน — tool answer
    state_mock = {"ok": True, "tool": "get_user_state", "stage": "1", "points": 5}
    c8 = classify("สถานะของฉัน", facts)
    d8 = route(c8, facts, state_mock, [])
    _check('"สถานะของฉัน" → TOOL_ANSWER', d8.route_type == RouteType.TOOL_ANSWER, f"got {d8.route_type}")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_arithmetic_direct_answer()
    test_memory_direct_from_facts()
    test_factual_goes_to_gemini_no_rag()
    test_normal_chat_goes_to_gemini()
    test_live_data_warning_and_no_invention()
    test_tool_queries_use_planner()
    test_fallback_no_state_dump()
    test_echo_not_in_gemini_context()
    test_memory_write_extraction()
    test_smoke_all_required()

    print(f"\n{'='*50}")
    print(f"Results: {_PASS} passed, {_FAIL} failed")

    if _FAIL > 0:
        sys.exit(1)

    print("All pipeline tests passed.")
    sys.exit(0)
