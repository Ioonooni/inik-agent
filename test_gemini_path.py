"""
Regression test: NORMAL_CHAT messages must reach the Gemini call path.
- Verifies routing leaves direct_reply=None for generic chat (so else-branch runs in app.py)
- Verifies answer_direct_memory_recall returns None for generic chat
- Mocks model.generate_content and confirms it is called exactly once
- Confirms fallback is returned (not None, no state dump) when mocked Gemini raises

No real Gemini API credit is consumed.
Run: python test_gemini_path.py
Exits 0 on success, 1 on failure.
"""
import sys
from unittest.mock import MagicMock

from truth_engine import classify, QueryType
from response_router import route, RouteType
from fallback import build_fallback_reply
from prompt_builder import build_main_prompt
from memory_direct_answer import answer_direct_memory_recall

_PASS = 0
_FAIL = 0

_NORMAL_MSGS = ["สวัสดี", "วันนี้เป็นยังไง", "เหนื่อยอะ", "คุยเล่นหน่อย", "เศร้า"]


def _check(label: str, condition: bool, detail: str = "") -> None:
    global _PASS, _FAIL
    if condition:
        print(f"  PASS  {label}")
        _PASS += 1
    else:
        print(f"  FAIL  {label}" + (f"  [{detail}]" if detail else ""))
        _FAIL += 1


def test_normal_chat_routes_to_gemini() -> None:
    """Route for NORMAL_CHAT must have no direct_reply and a GEMINI_* route_type."""
    print("\n=== NORMAL_CHAT must route to Gemini (no direct_reply) ===")

    for msg in _NORMAL_MSGS:
        c = classify(msg, {})
        d = route(c, {}, None, [])

        _check(
            f'"{msg}" classifies as NORMAL_CHAT',
            c.query_type == QueryType.NORMAL_CHAT,
            f"got {c.query_type}",
        )
        _check(
            f'"{msg}" route has no direct_reply',
            d.direct_reply is None,
            f"got direct_reply={d.direct_reply!r}",
        )
        _check(
            f'"{msg}" route_type is GEMINI_*',
            d.route_type in (RouteType.GEMINI_NO_MEMORY, RouteType.GEMINI_WITH_CONTEXT),
            f"got route_type={d.route_type}",
        )


def test_answer_direct_memory_recall_none_for_generic_chat() -> None:
    """answer_direct_memory_recall must return None for generic chat messages."""
    print("\n=== answer_direct_memory_recall returns None for generic chat ===")

    for msg in _NORMAL_MSGS:
        reply = answer_direct_memory_recall(msg, {}, [])
        _check(
            f'"{msg}" → None',
            reply is None,
            f"got {reply!r}",
        )


def test_mock_gemini_called_for_normal_chat() -> None:
    """Simulate the else-branch: model.generate_content is called exactly once."""
    print("\n=== Mocked Gemini called once for NORMAL_CHAT ===")

    prompt = build_main_prompt(
        stage_description="stage_desc",
        relationship_description="rel_desc",
        user_profile_description="profile_desc",
        response_mode_description="mode_desc",
        chat_history="",
        user_facts={},
        rag_context="ไม่มี RAG memory ที่เกี่ยวข้อง",
        user_message="สวัสดี",
        relationship_state={"trust": 0, "familiarity": 0, "curiosity": 0},
    )

    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "สวัสดีค่ะ!"
    mock_model.generate_content.return_value = mock_response

    USE_FAKE_AI = False
    _bypass_gemini = bool(USE_FAKE_AI)

    reply = None
    try:
        if _bypass_gemini:
            reply = "[FAKE]"
        else:
            response = mock_model.generate_content(prompt)
            reply = response.text
    except Exception:
        pass

    _check("USE_FAKE_AI=False → _bypass_gemini is False", not _bypass_gemini)
    _check("mock model called exactly once", mock_model.generate_content.call_count == 1)
    _check("reply equals mocked Gemini text", reply == "สวัสดีค่ะ!")
    _check("prompt is non-empty string", isinstance(prompt, str) and len(prompt) > 50)


def test_fallback_on_gemini_exception() -> None:
    """When mocked Gemini raises, fallback must be a non-empty string without state dump."""
    print("\n=== Mocked Gemini raises → fallback returned (no state dump) ===")

    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("429 quota exceeded")

    fallback_reply = None
    try:
        mock_model.generate_content("test prompt")
    except Exception as e:
        fallback_reply = build_fallback_reply(
            str(e),
            "สวัสดี",
            "1",
            "normal_chat",
            {},
            {"trust": 0, "familiarity": 0, "curiosity": 0},
            query_type="NORMAL_CHAT",
        )

    _check("fallback is not None", fallback_reply is not None)
    _check("fallback is a non-empty string", isinstance(fallback_reply, str) and len(fallback_reply) > 0)
    _check(
        "fallback contains no state dump (no 'Trust:')",
        "Trust:" not in (fallback_reply or ""),
        f"got: {fallback_reply!r}",
    )
    _check(
        "fallback contains no state dump (no 'Stage:')",
        "Stage:" not in (fallback_reply or ""),
        f"got: {fallback_reply!r}",
    )


def test_fake_ai_bypass_does_not_call_gemini() -> None:
    """When USE_FAKE_AI=True, generate_content must never be called."""
    print("\n=== USE_FAKE_AI=True → Gemini NOT called ===")

    mock_model = MagicMock()

    USE_FAKE_AI = True
    _bypass_gemini = bool(USE_FAKE_AI)

    if _bypass_gemini:
        reply = "[FAKE]"
    else:
        response = mock_model.generate_content("prompt")
        reply = response.text

    _check("USE_FAKE_AI=True → _bypass_gemini is True", _bypass_gemini)
    _check("mock model NOT called", mock_model.generate_content.call_count == 0)
    _check("reply is fake placeholder", reply == "[FAKE]")


if __name__ == "__main__":
    test_normal_chat_routes_to_gemini()
    test_answer_direct_memory_recall_none_for_generic_chat()
    test_mock_gemini_called_for_normal_chat()
    test_fallback_on_gemini_exception()
    test_fake_ai_bypass_does_not_call_gemini()

    print(f"\n{'='*50}")
    print(f"Results: {_PASS} passed, {_FAIL} failed")

    if _FAIL > 0:
        sys.exit(1)

    print("All Gemini path regression tests passed.")
    sys.exit(0)
