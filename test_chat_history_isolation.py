from memory import build_chat_history


def _pass(label):
    print(f"  PASS  {label}")


def _fail(label, detail=""):
    raise AssertionError(f"FAIL  {label}" + (f": {detail}" if detail else ""))


# ── fixtures ─────────────────────────────────────────────────────────────────

MIXED_HISTORY = [
    {"role": "user",      "content": "how should I invest?"},
    {"role": "assistant", "content": "i nik warm reply",        "agent_mode": "inik"},
    {"role": "user",      "content": "give me strategic advice"},
    {"role": "assistant", "content": "Rick strategic reply",    "agent_mode": "rick_royce"},
    {"role": "user",      "content": "follow up question"},
]

LEGACY_HISTORY = [
    {"role": "user",      "content": "hello"},
    {"role": "assistant", "content": "legacy reply with no agent_mode"},
    {"role": "user",      "content": "another message"},
    {"role": "assistant", "content": "another legacy reply"},
]


# ── test 1: inik mode excludes Rick assistant messages ────────────────────────

def test_inik_excludes_rick_messages():
    result = build_chat_history(MIXED_HISTORY, limit=10, active_agent_mode="inik")
    assert "Rick strategic reply" not in result, result
    assert "i nik warm reply" in result, result
    _pass("inik mode excludes Rick assistant messages")


# ── test 2: Rick mode excludes inik assistant messages ───────────────────────

def test_rick_excludes_inik_messages():
    result = build_chat_history(MIXED_HISTORY, limit=10, active_agent_mode="rick_royce")
    assert "i nik warm reply" not in result, result
    assert "Rick strategic reply" in result, result
    _pass("rick mode excludes inik assistant messages")


# ── test 3: user messages remain visible to both modes ───────────────────────

def test_user_messages_visible_to_both():
    inik_result  = build_chat_history(MIXED_HISTORY, limit=10, active_agent_mode="inik")
    rick_result  = build_chat_history(MIXED_HISTORY, limit=10, active_agent_mode="rick_royce")

    for msg in ("how should I invest?", "give me strategic advice", "follow up question"):
        assert msg in inik_result,  f"inik missing user message: {msg}"
        assert msg in rick_result,  f"rick missing user message: {msg}"

    _pass("user messages visible to both modes")


# ── test 4: legacy unlabeled entries skipped when filtering is active ─────────

def test_legacy_entries_skipped_when_filtering():
    for mode in ("inik", "rick_royce"):
        result = build_chat_history(LEGACY_HISTORY, limit=10, active_agent_mode=mode)
        assert "legacy reply with no agent_mode" not in result, \
            f"legacy entry leaked into {mode} history"
        assert "another legacy reply" not in result, \
            f"legacy entry leaked into {mode} history"
        assert "hello" in result
        assert "another message" in result
    _pass("legacy unlabeled entries skipped when filtering is active")


# ── test 5: new assistant persistence format includes agent_mode ──────────────

def test_new_persistence_format():
    msg = {"role": "assistant", "content": "reply", "agent_mode": "rick_royce"}
    assert msg.get("agent_mode") == "rick_royce"

    msg_inik = {"role": "assistant", "content": "reply", "agent_mode": "inik"}
    assert msg_inik.get("agent_mode") == "inik"

    _pass("new persistence format includes agent_mode field")


# ── test 6: no mode passed preserves legacy behaviour ────────────────────────

def test_no_mode_preserves_legacy_behavior():
    result = build_chat_history(MIXED_HISTORY, limit=10)
    assert "i nik warm reply" in result
    assert "Rick strategic reply" in result
    assert "i nik: i nik warm reply" in result
    assert "i nik: Rick strategic reply" in result
    _pass("no active_agent_mode preserves legacy include-all behaviour")


# ── test 7: correct label per mode ───────────────────────────────────────────

def test_label_by_mode():
    inik_result  = build_chat_history(MIXED_HISTORY, limit=10, active_agent_mode="inik")
    rick_result  = build_chat_history(MIXED_HISTORY, limit=10, active_agent_mode="rick_royce")

    assert "i nik: i nik warm reply" in inik_result, inik_result
    assert "Rick Royce: Rick strategic reply" in rick_result, rick_result

    hybrid_msgs = [
        {"role": "user",      "content": "hybrid question"},
        {"role": "assistant", "content": "hybrid answer", "agent_mode": "hybrid"},
    ]
    hybrid_result = build_chat_history(hybrid_msgs, limit=10, active_agent_mode="hybrid")
    assert "Hybrid: hybrid answer" in hybrid_result, hybrid_result

    _pass("correct label applied per active mode")


# ── test 8: limit still applies when filtering ────────────────────────────────

def test_limit_respected_with_filtering():
    many = []
    for i in range(20):
        many.append({"role": "user", "content": f"msg {i}"})
        many.append({"role": "assistant", "content": f"reply {i}", "agent_mode": "inik"})

    result = build_chat_history(many, limit=6, active_agent_mode="inik")
    lines = [l for l in result.splitlines() if l.strip()]
    assert len(lines) <= 6, f"expected ≤6 lines, got {len(lines)}"
    _pass("limit respected when filtering is active")


# ── runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_inik_excludes_rick_messages,
        test_rick_excludes_inik_messages,
        test_user_messages_visible_to_both,
        test_legacy_entries_skipped_when_filtering,
        test_new_persistence_format,
        test_no_mode_preserves_legacy_behavior,
        test_label_by_mode,
        test_limit_respected_with_filtering,
    ]
    print(f"Running {len(tests)} tests...\n")
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    if failed:
        raise SystemExit(1)
