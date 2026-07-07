"""
Tests for V3 contract restoration.

Verifies:
1. Omitted agent_mode defaults to "inik" (not "auto")
2. Omitted agent_mode is not in model_fields_set → preference not saved
3. Strategic message with omitted agent_mode → suggested_agent gate passes
4. Explicit rick_royce saves preferred_agent_mode
5. Explicit inik saves preferred_agent_mode (deliberate switch-back)

Uses a mirror model (_Req) instead of importing inik_api directly
because inik_api has dotenv/google-generativeai dependencies not available
in the test environment.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pydantic import BaseModel
from agent_router import classify_agent_route, detect_agent_handoff


# ── Mirror of ChatRequest with the restored default ─────────────────────────

class _Req(BaseModel):
    user_id: str = ""
    message: str
    agent_mode: str = "inik"


# ── 1. Default value and detection ──────────────────────────────────────────

def test_omitted_agent_mode_default_is_inik():
    """Pydantic default is "inik", not "auto"."""
    req = _Req.model_validate({"user_id": "u1", "message": "hello"})
    assert req.agent_mode == "inik"


def test_omitted_agent_mode_not_in_fields_set():
    """Omitted agent_mode is absent from model_fields_set → will not save preference."""
    req = _Req.model_validate({"user_id": "u1", "message": "hello"})
    assert "agent_mode" not in req.model_fields_set


# ── 2. Preference persistence gate ──────────────────────────────────────────

def _should_persist(req: _Req) -> bool:
    """Mirrors the persistence condition in inik_api.py."""
    agent_mode_explicit = "agent_mode" in req.model_fields_set
    return (
        agent_mode_explicit
        and req.agent_mode.strip().lower() in ("inik", "rick_royce", "hybrid")
    )


def test_omitted_mode_does_not_save_preference():
    """Omitted agent_mode → preference not saved."""
    req = _Req.model_validate({"user_id": "u1", "message": "ลงทุนหุ้น NVDA ดีไหม"})
    assert not _should_persist(req)


def test_explicit_rick_royce_saves_preference():
    """Explicit rick_royce → preference saved."""
    req = _Req.model_validate({"user_id": "u1", "message": "hi", "agent_mode": "rick_royce"})
    assert _should_persist(req)


def test_explicit_inik_saves_preference():
    """Explicit inik (user switching back) → preference saved."""
    req = _Req.model_validate({"user_id": "u1", "message": "hi", "agent_mode": "inik"})
    assert _should_persist(req)


def test_explicit_hybrid_saves_preference():
    """Explicit hybrid → preference saved."""
    req = _Req.model_validate({"user_id": "u1", "message": "hi", "agent_mode": "hybrid"})
    assert _should_persist(req)


def test_explicit_auto_does_not_save_preference():
    """Explicit "auto" → not a named mode → preference not saved."""
    req = _Req.model_validate({"user_id": "u1", "message": "hi", "agent_mode": "auto"})
    assert not _should_persist(req)


# ── 3. Routing: omitted agent_mode stays inik ────────────────────────────────

def test_omitted_mode_routes_to_inik_for_casual_message():
    """requested_mode="inik" → always inik for a normal message."""
    route = classify_agent_route("สวัสดีตอนเช้า", requested_mode="inik")
    assert route.agent_mode == "inik"


def test_omitted_mode_routes_to_inik_for_strategic_message():
    """requested_mode="inik" → stays inik even for a Rick-worthy message.
    Strategic topic surfaces through suggested_agent, not auto-routing."""
    route = classify_agent_route("ควรลงทุนใน NVDA ไหมตอนนี้", requested_mode="inik")
    assert route.agent_mode == "inik"


# ── 4. suggested_agent gate fires for strategic + omitted mode ───────────────

def test_strategic_message_produces_handoff_suggestion():
    """detect_agent_handoff returns non-None for investment message."""
    suggestion = detect_agent_handoff("ควรลงทุนใน NVDA ไหมตอนนี้")
    assert suggestion is not None


def test_suggested_agent_gate_passes_when_mode_is_inik():
    """Both conditions for suggested_agent to be non-null are met:
    agent_mode != "rick_royce" AND handoff_suggestion is non-None."""
    route = classify_agent_route("ควรลงทุนใน NVDA ไหมตอนนี้", requested_mode="inik")
    suggestion = detect_agent_handoff("ควรลงทุนใน NVDA ไหมตอนนี้")
    assert route.agent_mode != "rick_royce"
    assert suggestion is not None


def test_suggested_agent_gate_blocks_when_mode_is_rick():
    """When user explicitly chose rick_royce, agent_mode == rick_royce:
    the gate (agent_mode != rick_royce) is False → suggested_agent stays null."""
    route = classify_agent_route("ควรลงทุนใน NVDA ไหมตอนนี้", requested_mode="rick_royce")
    assert route.agent_mode == "rick_royce"
    # Gate condition is False → suggested_agent would be None


# ── 5. Preference restore path ───────────────────────────────────────────────

def _resolve_requested_mode(agent_mode_explicit: bool, raw: str, preferred: str | None) -> str:
    """Mirrors the routing branch in inik_api.py."""
    if agent_mode_explicit:
        return (raw or "inik").strip().lower()
    return (preferred or "inik").strip().lower()


def test_restore_uses_saved_preference_when_omitted():
    """Omitted + saved preference "rick_royce" → requested_mode resolved to rick_royce."""
    resolved = _resolve_requested_mode(False, "inik", "rick_royce")
    assert resolved == "rick_royce"


def test_restore_defaults_to_inik_when_no_preference():
    """Omitted + no saved preference → requested_mode resolved to inik."""
    resolved = _resolve_requested_mode(False, "inik", None)
    assert resolved == "inik"


def test_explicit_overrides_saved_preference():
    """Explicit "inik" overrides a saved "rick_royce" preference."""
    resolved = _resolve_requested_mode(True, "inik", "rick_royce")
    assert resolved == "inik"
