from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from behavior import get_stage
from rewards import check_reward
from relationship import update_relationship_state
from event_logger import send_event_to_n8n


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_get(session_state: Any, key: str, default: Any = None) -> Any:
    try:
        return session_state.get(key, default)
    except Exception:
        return default


def get_user_state(session_state: Any) -> Dict[str, Any]:
    intimacy_score = _safe_get(session_state, "intimacy_score", 0)

    return {
        "ok": True,
        "tool": "get_user_state",
        "timestamp": _now_iso(),
        "user_id": _safe_get(session_state, "user_id", "unknown_user"),
        "username": _safe_get(session_state, "username", "unknown"),
        "email": _safe_get(session_state, "email", None),
        "auth_mode": _safe_get(session_state, "auth_mode", "unknown"),
        "intimacy_score": intimacy_score,
        "stage": get_stage(intimacy_score),
        "points": _safe_get(session_state, "points", 0),
        "relationship_state": _safe_get(session_state, "relationship_state", {}),
        "memory_fact_count": len(_safe_get(session_state, "user_facts", {})),
        "inventory_count": len(_safe_get(session_state, "inventory", [])),
    }


def check_memory(session_state: Any, key: Optional[str] = None) -> Dict[str, Any]:
    user_facts = _safe_get(session_state, "user_facts", {})

    if key:
        return {
            "ok": True,
            "tool": "check_memory",
            "timestamp": _now_iso(),
            "key": key,
            "value": user_facts.get(key),
            "found": key in user_facts,
        }

    return {
        "ok": True,
        "tool": "check_memory",
        "timestamp": _now_iso(),
        "facts": user_facts,
        "fact_count": len(user_facts),
    }


def get_inventory(session_state: Any) -> Dict[str, Any]:
    inventory = _safe_get(session_state, "inventory", [])

    return {
        "ok": True,
        "tool": "get_inventory",
        "timestamp": _now_iso(),
        "inventory": inventory,
        "inventory_count": len(inventory),
    }


def get_visit_count(session_state: Any) -> Dict[str, Any]:
    user_profile = _safe_get(session_state, "user_profile", {})

    return {
        "ok": True,
        "tool": "get_visit_count",
        "timestamp": _now_iso(),
        "total_visits": user_profile.get("total_visits", 0),
        "total_messages": user_profile.get("total_messages", 0),
        "last_interaction_date": user_profile.get("last_interaction_date"),
    }


def get_relationship_state(session_state: Any) -> Dict[str, Any]:
    relationship_state = _safe_get(session_state, "relationship_state", {})

    return {
        "ok": True,
        "tool": "get_relationship_state",
        "timestamp": _now_iso(),
        "relationship_state": relationship_state,
        "trust": relationship_state.get("trust", 0),
        "familiarity": relationship_state.get("familiarity", 0),
        "curiosity": relationship_state.get("curiosity", 0),
    }


def update_relationship(session_state: Any, user_message: str) -> Dict[str, Any]:
    try:
        current_state = _safe_get(session_state, "relationship_state", {})
        updated_state = update_relationship_state(user_message, current_state)
        session_state.relationship_state = updated_state

        return {
            "ok": True,
            "tool": "update_relationship",
            "timestamp": _now_iso(),
            "relationship_state": updated_state,
        }

    except Exception as error:
        return {
            "ok": False,
            "tool": "update_relationship",
            "timestamp": _now_iso(),
            "error": str(error),
        }


def grant_points(
    session_state: Any,
    amount: int,
    reason: str = "tool_grant"
) -> Dict[str, Any]:
    try:
        if amount <= 0:
            return {
                "ok": False,
                "tool": "grant_points",
                "timestamp": _now_iso(),
                "error": "amount must be positive",
            }

        current_points = int(_safe_get(session_state, "points", 0))
        new_points = current_points + amount
        session_state.points = new_points

        reward = check_reward(new_points)

        if reward:
            inventory = list(_safe_get(session_state, "inventory", []))
            inventory.append(reward)
            session_state.inventory = inventory

        return {
            "ok": True,
            "tool": "grant_points",
            "timestamp": _now_iso(),
            "previous_points": current_points,
            "new_points": new_points,
            "amount": amount,
            "reason": reason,
            "reward": reward,
        }

    except Exception as error:
        return {
            "ok": False,
            "tool": "grant_points",
            "timestamp": _now_iso(),
            "error": str(error),
        }


def log_agent_event(
    session_state: Any,
    event_type: str,
    extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    try:
        result = send_event_to_n8n(
            event_type,
            session_state,
            extra=extra or {}
        )

        return {
            "ok": result.get("ok", False),
            "tool": "log_agent_event",
            "timestamp": _now_iso(),
            "event_type": event_type,
            "result": result,
        }

    except Exception as error:
        return {
            "ok": False,
            "tool": "log_agent_event",
            "timestamp": _now_iso(),
            "event_type": event_type,
            "error": str(error),
        }


def list_available_tools() -> List[Dict[str, str]]:
    return [
        {
            "name": "get_user_state",
            "description": "Read current user state, auth mode, stage, points, and memory count.",
        },
        {
            "name": "check_memory",
            "description": "Read all remembered facts or one specific memory key.",
        },
        {
            "name": "get_inventory",
            "description": "Read user inventory and item count.",
        },
        {
            "name": "get_visit_count",
            "description": "Read total visits, total messages, and last interaction date.",
        },
        {
            "name": "get_relationship_state",
            "description": "Read trust, familiarity, curiosity, and relationship state.",
        },
        {
            "name": "update_relationship",
            "description": "Update relationship state from a user message.",
        },
        {
            "name": "grant_points",
            "description": "Grant points and trigger reward logic if eligible.",
        },
        {
            "name": "log_agent_event",
            "description": "Log an agent event to Supabase and optionally n8n.",
        },
    ]


def run_tool(
    tool_name: str,
    session_state: Any,
    arguments: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    arguments = arguments or {}

    tool_map = {
        "get_user_state": lambda: get_user_state(session_state),
        "check_memory": lambda: check_memory(
            session_state,
            key=arguments.get("key")
        ),
        "get_inventory": lambda: get_inventory(session_state),
        "get_visit_count": lambda: get_visit_count(session_state),
        "get_relationship_state": lambda: get_relationship_state(session_state),
        "update_relationship": lambda: update_relationship(
            session_state,
            user_message=arguments.get("user_message", "")
        ),
        "grant_points": lambda: grant_points(
            session_state,
            amount=int(arguments.get("amount", 1)),
            reason=arguments.get("reason", "tool_grant")
        ),
        "log_agent_event": lambda: log_agent_event(
            session_state,
            event_type=arguments.get("event_type", "agent_tool_event"),
            extra=arguments.get("extra", {})
        ),
    }

    if tool_name not in tool_map:
        return {
            "ok": False,
            "tool": tool_name,
            "timestamp": _now_iso(),
            "error": f"Unknown tool: {tool_name}",
            "available_tools": [tool["name"] for tool in list_available_tools()],
        }

    return tool_map[tool_name]()


if __name__ == "__main__":
    for tool in list_available_tools():
        print(f"{tool['name']}: {tool['description']}")