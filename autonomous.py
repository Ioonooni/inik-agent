from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from agent_tools import run_tool


_ACTION_COOLDOWNS = {
    "ask_memory_seed": timedelta(hours=24),
    "suggest_reward_check": timedelta(hours=24),
    "relationship_checkpoint": timedelta(hours=24),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _action_on_cooldown(session_state: Any, action: str) -> bool:
    last_fired = (session_state.get("_autonomous_action_last_fired") or {}).get(action)
    if last_fired is None:
        return False
    cooldown = _ACTION_COOLDOWNS.get(action, timedelta(hours=1))
    return datetime.now(timezone.utc) - last_fired < cooldown


def _mark_action_fired(session_state: Any, action: str) -> None:
    if "_autonomous_action_last_fired" not in session_state:
        session_state["_autonomous_action_last_fired"] = {}
    session_state["_autonomous_action_last_fired"][action] = datetime.now(timezone.utc)


def build_autonomous_decision(session_state: Any) -> Dict:
    points = session_state.get("points", 0)
    intimacy_score = session_state.get("intimacy_score", 0)
    inventory = session_state.get("inventory", [])
    user_facts = session_state.get("user_facts", {})

    if not user_facts:
        return {
            "should_act": True,
            "action": "ask_memory_seed",
            "reason": "ผู้ใช้ยังไม่มีข้อมูลที่จำได้เลย i nik ควรถามเพื่อรู้จักมากขึ้น",
            "fallback_message": "ฉันยังรู้น้อยเกี่ยวกับเธออยู่เลย มนุษย์คนนี้มีอะไรที่ควรจำบ้างนะ",
            "tool": "log_agent_event",
            "arguments": {
                "event_type": "autonomous_memory_seed_suggested",
                "extra": {"reason": "empty_user_facts"},
            },
        }

    if points >= 10 and not inventory:
        return {
            "should_act": True,
            "action": "suggest_reward_check",
            "reason": f"ผู้ใช้มี {points} แต้มแล้วแต่ยังไม่มีของใน inventory เลย",
            "fallback_message": "แต้มเธอเริ่มน่าสนใจแล้วนะ เหมือนมีอะไรบางอย่างควรโผล่มาในร้านนี้",
            "tool": "log_agent_event",
            "arguments": {
                "event_type": "autonomous_reward_suggested",
                "extra": {"points": points},
            },
        }

    if intimacy_score >= 50:
        return {
            "should_act": True,
            "action": "relationship_checkpoint",
            "reason": f"ความสนิทถึง {intimacy_score} แล้ว i nik ควรพูดถึงพัฒนาการของความสัมพันธ์",
            "fallback_message": "เราเริ่มคุยกันบ่อยพอที่ฉันจำจังหวะของเธอได้มากขึ้นแล้วนะ",
            "tool": "log_agent_event",
            "arguments": {
                "event_type": "autonomous_relationship_checkpoint",
                "extra": {"intimacy_score": intimacy_score},
            },
        }

    return {
        "should_act": False,
        "action": "no_action",
        "reason": "No autonomous action needed.",
        "fallback_message": None,
        "tool": None,
        "arguments": {},
    }


def _generate_autonomous_message(model: Any, reason: str) -> Optional[str]:
    try:
        prompt = (
            "เธอคือ i nik pixie ประจำร้าน ตัวเล็ก ช่างสังเกต ซนนิดหน่อย\n"
            f"เธอสังเกตว่า: {reason}\n"
            "พูดเป็นธรรมชาติสั้น ๆ 1-2 ประโยค ในแบบของ i nik "
            "ห้ามใช้ภาษาทางการ ห้ามอธิบายว่ากำลังทำอะไรอยู่"
        )
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        return text if text else None
    except Exception:
        return None


def run_autonomous_check(session_state: Any, model: Any = None) -> Dict:
    decision = build_autonomous_decision(session_state)

    # Deduplicate: suppress actions that are still on cooldown
    if decision.get("should_act"):
        action = decision.get("action", "")
        if _action_on_cooldown(session_state, action):
            decision["should_act"] = False
            decision["message"] = None
            return {
                "ok": True,
                "timestamp": now_iso(),
                "decision": decision,
                "tool_result": None,
            }

        if model:
            ai_msg = _generate_autonomous_message(model, decision["reason"])
            decision["message"] = ai_msg or decision["fallback_message"]
        else:
            decision["message"] = decision["fallback_message"]

        _mark_action_fired(session_state, action)
    else:
        decision["message"] = None

    tool_result = None
    if decision.get("should_act") and decision.get("tool"):
        tool_result = run_tool(
            decision["tool"],
            session_state,
            decision.get("arguments", {}),
        )

    return {
        "ok": True,
        "timestamp": now_iso(),
        "decision": decision,
        "tool_result": tool_result,
    }


if __name__ == "__main__":
    print("autonomous v2 ready")
