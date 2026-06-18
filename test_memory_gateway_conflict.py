"""
Phase 4.3 — conflict detection + soft-supersede on the write path.

supabase_memory / supabase_memory_v2 are stubbed before import so the module
loads without streamlit. All Supabase callsites are patched per test.
"""
import sys
from unittest.mock import MagicMock, patch

for _m in ("supabase_memory", "supabase_memory_v2"):
    sys.modules.setdefault(_m, MagicMock())

from memory_gateway_v2 import save_message_memory_v2  # noqa: E402


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OLD_TS    = "2020-01-01T00:00:00+00:00"
FUTURE_TS = "2099-01-01T00:00:00+00:00"

# Both messages start with "ฉันชอบ" → "preference" conflict category, type user_fact
PREF_MSG_A = "ฉันชอบดาวเสาร์"
PREF_MSG_B = "ฉันชอบดาวพฤหัส"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _existing(content, *, ts=OLD_TS, user_id="u1",
              memory_type="user_fact", memory_id=None) -> dict:
    from memory_schema import make_memory_id
    return {
        "memory_id": memory_id or make_memory_id(user_id, content, memory_type),
        "user_id": user_id,
        "content": content,
        "memory_type": memory_type,
        "importance": 80,
        "hit_count": 1,
        "last_seen_at": ts,
        "created_at": ts,
        "metadata": {},
    }


def _run(message, *, user_id="u1", existing=None,
         fetch_raises=False, supersede_raises=False, supabase_raises=False,
         fake_record=None):
    """
    Drive save_message_memory_v2 with all Supabase callsites mocked.

    Returns (result, fetch_mock, upsert_mock, supersede_mock).
    """
    mock_client = MagicMock()

    fetch_mock = MagicMock()
    if fetch_raises:
        fetch_mock.side_effect = Exception("fetch failed")
    else:
        fetch_mock.return_value = list(existing or [])

    supersede_mock = MagicMock()
    if supersede_raises:
        supersede_mock.side_effect = Exception("writeback failed")
    else:
        supersede_mock.return_value = {"ok": True}

    upsert_mock = MagicMock(
        return_value={"ok": True, "memory_id": "x", "result": MagicMock()}
    )
    local_upsert_mock = MagicMock(return_value={"ok": True})

    if supabase_raises:
        client_ctx = patch("memory_gateway_v2.get_supabase_client",
                           side_effect=Exception("no supabase"))
    else:
        client_ctx = patch("memory_gateway_v2.get_supabase_client",
                           return_value=mock_client)

    patches = [
        client_ctx,
        patch("memory_gateway_v2.fetch_conflictable_memories", fetch_mock),
        patch("memory_gateway_v2.upsert_supabase_memory", upsert_mock),
        patch("memory_gateway_v2.supersede_supabase_memory", supersede_mock),
        patch("memory_gateway_v2.upsert_memory_record", local_upsert_mock),
    ]
    if fake_record is not None:
        patches.append(
            patch("memory_gateway_v2.build_memory_from_message",
                  return_value=fake_record)
        )

    result = None
    ctx_stack = []
    for p in patches:
        ctx_stack.append(p.__enter__())
    try:
        result = save_message_memory_v2(user_id=user_id, message=message)
    finally:
        for i, p in enumerate(reversed(patches)):
            p.__exit__(None, None, None)

    return result, fetch_mock, upsert_mock, supersede_mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_non_conflictable_type_skips_check():
    """conversation_event memory type → conflict check skipped entirely."""
    fake = {
        "memory_id": "aabbccddeeff00112233",
        "user_id": "u1",
        "content": "some chat message",
        "memory_type": "conversation_event",
        "importance": 50,
        "source": "chat",
        "schema_version": "memory_v2",
        "created_at": OLD_TS,
        "last_seen_at": OLD_TS,
        "hit_count": 1,
        "metadata": {},
    }
    result, fetch_mock, upsert_mock, _ = _run(
        "whatever", fake_record=fake
    )

    assert result["ok"] is True
    assert result["backend"] == "supabase"
    cs = result["conflict_summary"]
    assert cs["checked"] is False
    assert cs["reason"] == "non_conflictable_type"
    fetch_mock.assert_not_called()
    upsert_mock.assert_called_once()


def test_no_existing_memories_no_supersede():
    """No conflictable memories in Supabase → supersede=0, save proceeds."""
    result, fetch_mock, upsert_mock, supersede_mock = _run(
        PREF_MSG_A, existing=[]
    )

    assert result["ok"] is True
    assert result["backend"] == "supabase"
    cs = result["conflict_summary"]
    assert cs["checked"] is True
    assert cs["superseded"] == 0
    supersede_mock.assert_not_called()
    upsert_mock.assert_called_once()


def test_incoming_newer_supersedes_existing():
    """Incoming is newer → existing same-category memory is soft-superseded."""
    existing = [_existing(PREF_MSG_B, ts=OLD_TS)]  # older timestamp
    result, _, upsert_mock, supersede_mock = _run(
        PREF_MSG_A, existing=existing       # incoming has ts=now > OLD_TS
    )

    assert result["ok"] is True
    assert result["backend"] == "supabase"
    cs = result["conflict_summary"]
    assert cs["checked"] is True
    assert cs["superseded"] == 1
    supersede_mock.assert_called_once()
    # Only metadata should be updated — verify memory_id passed
    _, kwargs = supersede_mock.call_args
    assert kwargs.get("memory_id") == existing[0]["memory_id"] or \
           supersede_mock.call_args[0][1] == existing[0]["memory_id"]
    upsert_mock.assert_called_once()


def test_existing_newer_no_supersede():
    """Existing has a future timestamp (newer) → incoming does NOT win → no supersede."""
    existing = [_existing(PREF_MSG_B, ts=FUTURE_TS)]  # newer than incoming
    result, _, upsert_mock, supersede_mock = _run(
        PREF_MSG_A, existing=existing
    )

    assert result["ok"] is True
    cs = result["conflict_summary"]
    assert cs["checked"] is True
    assert cs["superseded"] == 0
    supersede_mock.assert_not_called()
    upsert_mock.assert_called_once()


def test_same_memory_id_not_superseded():
    """Existing memory with the same memory_id as incoming is skipped (self-match)."""
    from memory_schema import make_memory_id
    shared_id = make_memory_id("u1", PREF_MSG_A, "user_fact")
    existing = [_existing(PREF_MSG_A, ts=OLD_TS, memory_id=shared_id)]

    result, _, upsert_mock, supersede_mock = _run(
        PREF_MSG_A, existing=existing
    )

    assert result["ok"] is True
    cs = result["conflict_summary"]
    assert cs["checked"] is True
    assert cs["superseded"] == 0
    supersede_mock.assert_not_called()
    upsert_mock.assert_called_once()


def test_fetch_failure_does_not_block_save():
    """If fetch_conflictable_memories raises, save must still succeed."""
    result, fetch_mock, upsert_mock, supersede_mock = _run(
        PREF_MSG_A, fetch_raises=True
    )

    assert result["ok"] is True
    assert result["backend"] == "supabase"
    cs = result["conflict_summary"]
    assert cs["checked"] is False
    assert "error" in cs
    upsert_mock.assert_called_once()
    supersede_mock.assert_not_called()


def test_supersede_writeback_failure_does_not_block_save():
    """If supersede write-back raises, the upsert of incoming must still complete."""
    existing = [_existing(PREF_MSG_B, ts=OLD_TS)]
    result, _, upsert_mock, supersede_mock = _run(
        PREF_MSG_A, existing=existing, supersede_raises=True
    )

    assert result["ok"] is True
    assert result["backend"] == "supabase"
    cs = result["conflict_summary"]
    assert cs["checked"] is True
    assert cs["superseded"] == 0          # write-back failed → not counted
    assert "writeback_errors" in cs       # error is recorded
    upsert_mock.assert_called_once()


def test_local_fallback_has_conflict_summary_unchecked():
    """When Supabase is unavailable, local_fallback response carries the expected conflict_summary."""
    result, fetch_mock, _, _ = _run(
        PREF_MSG_A, supabase_raises=True
    )

    assert result["ok"] is True
    assert result["backend"] == "local_fallback"
    cs = result["conflict_summary"]
    assert cs["checked"] is False
    assert cs["reason"] == "supabase_unavailable_local_fallback"
    fetch_mock.assert_not_called()
