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
            f'"{msg}" → STRUCTURED_MEMORY',
            d.route_type == RouteType.STRUCTURED_MEMORY,
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
            f'"{msg}" → GEMINI_NO_MEMORY',
            d.route_type == RouteType.GEMINI_NO_MEMORY,
            f"got {d.route_type}",
        )
        _check(
            f'"{msg}" → no direct_reply (no invention)',
            d.direct_reply is None,
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
    print("\n=== Fallback must NOT dump user state for ANY query type ===")

    user_facts = {"name": "ไออุ่น"}
    rel_state = {"trust": 30, "familiarity": 20, "curiosity": 10}
    state_markers = ["Trust:", "Familiarity:", "Stage:", "Curiosity:"]

    # ALL known query types must never leak state
    for qtype in ("FACTUAL_QUERY", "NORMAL_CHAT", "MEMORY_QUERY", "TOOL_QUERY", "RELATIONSHIP_QUERY", None):
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
                    f'{str(qtype)}/{err[:10]} fallback has no "{marker}"',
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
    _check('"2+2 เท่ากับเท่าไหร่" → STRUCTURED_MEMORY', d6.route_type == RouteType.STRUCTURED_MEMORY, f"got {d6.route_type}")
    _check('"2+2 เท่ากับเท่าไหร่" → answer = 4', d6.direct_reply == "4", f"got {d6.direct_reply}")

    # 7. วันนี้อากาศเป็นไง — live data, must not invent, must get warning
    c7 = classify("วันนี้อากาศเป็นไง", facts)
    d7 = route(c7, facts, None, [])
    _check('"วันนี้อากาศเป็นไง" → live_data_warning', d7.live_data_warning is not None, f"got {d7.live_data_warning}")
    _check('"วันนี้อากาศเป็นไง" → GEMINI_NO_MEMORY', d7.route_type == RouteType.GEMINI_NO_MEMORY, f"got {d7.route_type}")
    _check('"วันนี้อากาศเป็นไง" → no direct_reply', d7.direct_reply is None, f"got {d7.direct_reply}")

    # 8. สถานะของฉัน — tool answer
    state_mock = {"ok": True, "tool": "get_user_state", "stage": "1", "points": 5}
    c8 = classify("สถานะของฉัน", facts)
    d8 = route(c8, facts, state_mock, [])
    _check('"สถานะของฉัน" → TOOL_ANSWER', d8.route_type == RouteType.TOOL_ANSWER, f"got {d8.route_type}")


# ---------------------------------------------------------------------------
# 11. Adversarial: stored preference must NEVER contaminate factual answers
# ---------------------------------------------------------------------------
def test_adversarial_no_memory_contamination() -> None:
    print("\n=== ADVERSARIAL: stored preference must not contaminate factual queries ===")

    # Scenario A: user says they like black holes, then asks what black holes are
    facts_bh = {"name": "ไออุ่น", "likes": "หลุมดำ"}
    echo_bh = [{"content": "ฉันชอบหลุมดำ", "memory_type": "user_message"}]
    verified_bh = verify(echo_bh)

    for msg in ["หลุมดำคืออะไร", "เล่าเรื่องหลุมดำ"]:
        c = classify(msg, facts_bh)
        d = route(c, facts_bh, None, verified_bh)
        _check(
            f'[likes=หลุมดำ] "{msg}" must be FACTUAL (not MEMORY)',
            c.query_type == QueryType.FACTUAL_QUERY,
            f"got {c.query_type}",
        )
        _check(
            f'[likes=หลุมดำ] "{msg}" → GEMINI_NO_MEMORY',
            d.route_type == RouteType.GEMINI_NO_MEMORY,
            f"got {d.route_type}",
        )
        _check(
            f'[likes=หลุมดำ] "{msg}" no direct_reply',
            d.direct_reply is None,
            f"got {d.direct_reply}",
        )
        _check(
            f'[likes=หลุมดำ] "{msg}" no memory RAG',
            "เธอเคยพูดว่า" not in d.rag_context,
            f"rag={d.rag_context}",
        )

    # Scenario B: user likes Saturn, then asks factual Saturn questions
    facts_sat = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}
    echo_sat = [{"content": "ฉันชอบดาวเสาร์", "memory_type": "user_message"}]
    verified_sat = verify(echo_sat)

    for msg in ["ดาวเสาร์คืออะไร", "เล่าเรื่องดาวเสาร์", "ดาวเสาร์อยู่ห่างโลกแค่ไหน"]:
        c = classify(msg, facts_sat)
        d = route(c, facts_sat, None, verified_sat)
        _check(
            f'[likes=ดาวเสาร์] "{msg}" must not be MEMORY_QUERY',
            c.query_type != QueryType.MEMORY_QUERY,
            f"got {c.query_type}",
        )
        _check(
            f'[likes=ดาวเสาร์] "{msg}" no direct memory reply',
            d.direct_reply is None or "ดาวเสาร์" not in (d.direct_reply or ""),
            f"got {d.direct_reply}",
        )

    # Scenario C: user sets name, asks completely unrelated factual question
    facts_name = {"name": "ไออุ่น"}
    for msg in ["โลกกลมไหม", "หลุมดำคืออะไร", "อธิบายควอนตัม"]:
        c = classify(msg, facts_name)
        d = route(c, facts_name, None, [])
        _check(
            f'[name=ไออุ่น] "{msg}" must be FACTUAL',
            c.query_type == QueryType.FACTUAL_QUERY,
            f"got {c.query_type}",
        )
        _check(
            f'[name=ไออุ่น] "{msg}" must not mention ไออุ่น in direct_reply',
            "ไออุ่น" not in (d.direct_reply or ""),
            f"got {d.direct_reply}",
        )


# ---------------------------------------------------------------------------
# 12. Adversarial: classification edge cases and Thai language variants
# ---------------------------------------------------------------------------
def test_adversarial_classification_edge_cases() -> None:
    print("\n=== ADVERSARIAL: edge cases and Thai variants ===")

    facts = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}

    # Memory questions in various Thai question forms
    memory_forms = [
        "ชื่อฉันคืออะไร",
        "จำชื่อฉันได้ไหม",
        "ชื่อฉันคืออะไรนะ",
        "รู้จักชื่อฉันไหม",
    ]
    for msg in memory_forms:
        c = classify(msg, facts)
        _check(
            f'memory question "{msg}" → MEMORY_QUERY',
            c.query_type == QueryType.MEMORY_QUERY,
            f"got {c.query_type}",
        )

    # Inventory query variants
    inventory_forms = ["ฉันมีของอะไรบ้าง", "สถานะของฉัน", "คะแนนของฉันเท่าไร"]
    for msg in inventory_forms:
        c = classify(msg, {})
        _check(
            f'state query "{msg}" → TOOL_QUERY or RELATIONSHIP_QUERY',
            c.query_type in (QueryType.TOOL_QUERY, QueryType.RELATIONSHIP_QUERY),
            f"got {c.query_type}",
        )

    # Ambiguous inputs must NOT be MEMORY_QUERY
    ambiguous = ["ดาวเสาร์", "หลุมดำ", "เศร้าอะ", "เหนื่อยจัง"]
    for msg in ambiguous:
        c = classify(msg, facts)
        _check(
            f'ambiguous "{msg}" must not be MEMORY_QUERY',
            c.query_type != QueryType.MEMORY_QUERY,
            f"got {c.query_type}",
        )

    # Negative arithmetic
    arith_neg = [("-5+2", "-3"), ("-10*2", "-20")]
    from truth_engine import _try_eval_math
    for expr, expected in arith_neg:
        result = _try_eval_math(expr)
        _check(
            f'negative math "{expr}" = "{expected}"',
            result == expected,
            f"got {result}",
        )


# ---------------------------------------------------------------------------
# 13. None-safe direct_reply guard
# ---------------------------------------------------------------------------
def test_structured_memory_never_none() -> None:
    print("\n=== STRUCTURED_MEMORY direct_reply must never be None ===")

    # When facts has the key, direct_reply must be a string
    facts = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}
    for msg in ["ฉันชื่ออะไร", "ฉันชอบอะไร"]:
        c = classify(msg, facts)
        d = route(c, facts, None, [])
        if d.route_type == RouteType.STRUCTURED_MEMORY:
            _check(
                f'"{msg}" STRUCTURED_MEMORY direct_reply is non-empty string',
                isinstance(d.direct_reply, str) and len(d.direct_reply) > 0,
                f"got {d.direct_reply!r}",
            )

    # Arithmetic STRUCTURED_MEMORY direct_reply is always a string
    for msg, expected in [("2+2", "4"), ("10-3", "7")]:
        c = classify(msg, {})
        d = route(c, {}, None, [])
        _check(
            f'arithmetic "{msg}" direct_reply = "{expected}"',
            d.direct_reply == expected,
            f"got {d.direct_reply!r}",
        )


# ---------------------------------------------------------------------------
# 14. Full acceptance test matrix (all required cases from spec)
# ---------------------------------------------------------------------------
def test_full_acceptance_matrix() -> None:
    print("\n=== FULL ACCEPTANCE MATRIX ===")

    from facts import extract_facts

    facts = {}
    facts = extract_facts("ฉันชื่อไออุ่น", facts)
    facts = extract_facts("ฉันชอบดาวเสาร์", facts)
    state_mock = {"ok": True, "tool": "get_user_state", "stage": "1", "points": 5}
    inv_mock   = {"ok": True, "tool": "get_inventory",  "inventory": []}
    rel_mock   = {"ok": True, "tool": "get_relationship_state", "trust": 10}

    matrix = [
        # (message, facts_to_use, planner_mock, check_fn_label, check_fn)
        ("ฉันชื่ออะไร",            facts, None,       "STRUCTURED_MEMORY+ไออุ่น",
            lambda c, d: d.route_type == RouteType.STRUCTURED_MEMORY and "ไออุ่น" in (d.direct_reply or "")),
        ("ชื่อฉันคืออะไร",          facts, None,       "STRUCTURED_MEMORY+ไออุ่น",
            lambda c, d: d.route_type == RouteType.STRUCTURED_MEMORY and "ไออุ่น" in (d.direct_reply or "")),
        ("ฉันชอบอะไร",             facts, None,       "STRUCTURED_MEMORY+ดาวเสาร์",
            lambda c, d: d.route_type == RouteType.STRUCTURED_MEMORY and "ดาวเสาร์" in (d.direct_reply or "")),
        ("จำอะไรได้บ้าง",          facts, None,       "MEMORY_QUERY",
            lambda c, d: c.query_type == QueryType.MEMORY_QUERY),
        ("2+2 เท่ากับเท่าไร",       {},    None,       "direct=4",
            lambda c, d: d.direct_reply == "4"),
        ("15*3",                   {},    None,       "direct=45",
            lambda c, d: d.direct_reply == "45"),
        ("โลกกลมไหม",              {},    None,       "GEMINI_NO_MEMORY",
            lambda c, d: d.route_type == RouteType.GEMINI_NO_MEMORY and d.direct_reply is None),
        ("หลุมดำคืออะไร",           {},    None,       "GEMINI_NO_MEMORY",
            lambda c, d: d.route_type == RouteType.GEMINI_NO_MEMORY),
        ("ดาวเสาร์คืออะไร",         facts, None,       "GEMINI_NO_MEMORY (not memory)",
            lambda c, d: d.route_type == RouteType.GEMINI_NO_MEMORY and c.query_type == QueryType.FACTUAL_QUERY),
        ("เล่าเรื่องหลุมดำ",         facts, None,       "GEMINI_NO_MEMORY",
            lambda c, d: d.route_type == RouteType.GEMINI_NO_MEMORY),
        ("เล่าเรื่องดาวเสาร์",       facts, None,       "GEMINI_NO_MEMORY (not memory)",
            lambda c, d: d.route_type == RouteType.GEMINI_NO_MEMORY and c.query_type == QueryType.FACTUAL_QUERY),
        ("วันนี้อากาศเป็นไง",        {},    None,       "live_data_warning",
            lambda c, d: d.live_data_warning is not None and d.direct_reply is None),
        ("ตอนนี้กี่โมง",             {},    None,       "live_data_warning",
            lambda c, d: d.live_data_warning is not None),
        ("ราคาทองวันนี้เท่าไร",      {},    None,       "live_data_warning",
            lambda c, d: d.live_data_warning is not None),
        ("สถานะของฉัน",             {},    state_mock, "TOOL_ANSWER",
            lambda c, d: d.route_type == RouteType.TOOL_ANSWER),
        ("คะแนนของฉันเท่าไร",       {},    state_mock, "TOOL_ANSWER",
            lambda c, d: d.route_type == RouteType.TOOL_ANSWER),
        ("ฉันมีของอะไรบ้าง",         {},    inv_mock,   "TOOL_ANSWER",
            lambda c, d: d.route_type == RouteType.TOOL_ANSWER),
        ("ความสัมพันธ์ตอนนี้เป็นไง", {},    rel_mock,   "TOOL_ANSWER",
            lambda c, d: d.route_type == RouteType.TOOL_ANSWER),
        ("เหนื่อยอะ",               {},    None,       "NORMAL_CHAT no direct_reply",
            lambda c, d: c.query_type == QueryType.NORMAL_CHAT and d.direct_reply is None),
        ("คุยเล่นหน่อย",            {},    None,       "NORMAL_CHAT no direct_reply",
            lambda c, d: c.query_type == QueryType.NORMAL_CHAT and d.direct_reply is None),
        ("วันนี้เบื่อจัง",           {},    None,       "NORMAL_CHAT no direct_reply",
            lambda c, d: c.query_type == QueryType.NORMAL_CHAT and d.direct_reply is None),
    ]

    for msg, f, mock, label, check in matrix:
        c = classify(msg, f)
        d = route(c, f, mock, [])
        _check(f'"{msg}" → {label}', check(c, d), f"query={c.query_type} route={d.route_type} reply={d.direct_reply!r}")


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
    test_adversarial_no_memory_contamination()
    test_adversarial_classification_edge_cases()
    test_structured_memory_never_none()
    test_full_acceptance_matrix()

    print(f"\n{'='*50}")
    print(f"Results: {_PASS} passed, {_FAIL} failed")

    if _FAIL > 0:
        sys.exit(1)

    print("All pipeline tests passed.")
    sys.exit(0)
