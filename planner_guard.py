from typing import Any, Dict, Optional

from agent_tools import list_available_tools


AVAILABLE_TOOL_NAMES = {tool["name"] for tool in list_available_tools()}


def normalize_plan(plan: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(plan, dict):
        return {
            "goal": "normal_chat",
            "tool": None,
            "arguments": {},
            "ok": False,
            "reason": "invalid_plan_type",
        }

    goal = plan.get("goal") or "normal_chat"
    tool = plan.get("tool")
    arguments = plan.get("arguments")

    if arguments is None:
        arguments = {}

    if not isinstance(arguments, dict):
        arguments = {}

    if tool is not None and tool not in AVAILABLE_TOOL_NAMES:
        return {
            "goal": "normal_chat",
            "tool": None,
            "arguments": {},
            "ok": False,
            "reason": f"unknown_tool:{tool}",
        }

    return {
        "goal": str(goal),
        "tool": tool,
        "arguments": arguments,
        "ok": True,
        "reason": "ok",
    }
