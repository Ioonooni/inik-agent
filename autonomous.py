from datetime import datetime, timezone
from typing import Any, Dict

from agent_tools import run_tool


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_autonomous_decision(session_state: Any) -> Dict:
    points = session_state.get("points", 0)
    intimacy_score = session_state.get("intimacy_score", 0)
    inventory = session_state.get("inventory", [])
    user_facts = session_state.get("user_facts", {})

    if not user_facts:
        return {
            "should_act": True,
            "action": "ask_memory_seed",
            "reason": "User has no remembered facts yet.",
            "message": "ฉันยังรู้น้อยเกี่ยวกับเธออยู่เลย มนุษย์คนนี้มีอะไรที่ควรจำบ้างนะ",
            "tool": "log_agent_event",
            "arguments": {
                "event_type": "autonomous_memory_seed_suggested",
                "extra": {"reason": "empty_user_facts"}
            }
        }

    if points >= 10 and not inventory:
        return {
            "should_act": True,
            "action": "suggest_reward_check",
            "reason": "User has enough points but no inventory.",
            "message": "แต้มเธอเริ่มน่าสนใจแล้วนะ เหมือนมีอะไรบางอย่างควรโผล่มาในร้านนี้",
            "tool": "log_agent_event",
            "arguments": {
                "event_type": "autonomous_reward_suggested",
                "extra": {"points": points}
            }
        }

    if intimacy_score >= 50:
        return {
            "should_act": True,
            "action": "relationship_checkpoint",
            "reason": "User intimacy reached meaningful threshold.",
            "message": "เราเริ่มคุยกันบ่อยพอที่ฉันจำจังหวะของเธอได้มากขึ้นแล้วนะ",
            "tool": "log_agent_event",
            "arguments": {
                "event_type": "autonomous_relationship_checkpoint",
                "extra": {"intimacy_score": intimacy_score}
            }
        }

    return {
        "should_act": False,
        "action": "no_action",
        "reason": "No autonomous action needed.",
        "message": None,
        "tool": None,
        "arguments": {}
    }


def run_autonomous_check(session_state: Any) -> Dict:
    decision = build_autonomous_decision(session_state)

    tool_result = None

    if decision.get("should_act") and decision.get("tool"):
        tool_result = run_tool(
            decision["tool"],
            session_state,
            decision.get("arguments", {})
        )

    return {
        "ok": True,
        "timestamp": now_iso(),
        "decision": decision,
        "tool_result": tool_result
    }


if __name__ == "__main__":
    print("autonomous trigger v1 ready")