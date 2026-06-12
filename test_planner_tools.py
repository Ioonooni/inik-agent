from planner import build_plan
from agent_tools import list_available_tools


class Session(dict):
    pass


AVAILABLE_TOOL_NAMES = {tool["name"] for tool in list_available_tools()}


def assert_valid_plan(message: str, expected_tool: str | None):
    plan = build_plan(message, Session())

    assert isinstance(plan, dict), plan
    assert "goal" in plan, plan
    assert "tool" in plan, plan
    assert "arguments" in plan, plan
    assert isinstance(plan["arguments"], dict), plan

    if expected_tool is None:
        assert plan["tool"] is None, plan
    else:
        assert plan["tool"] == expected_tool, plan
        assert plan["tool"] in AVAILABLE_TOOL_NAMES, plan


assert_valid_plan("ฉันชื่ออะไร", "check_memory")
assert_valid_plan("ฉันชอบอะไร", "check_memory")
assert_valid_plan("คะแนนของฉันเท่าไร", "get_user_state")
assert_valid_plan("ดูของรางวัลที่ได้", "get_inventory")
assert_valid_plan("ความสัมพันธ์ตอนนี้เป็นไง", "get_relationship_state")
assert_valid_plan("วันนี้อยากคุยเล่น", None)

print("PLANNER TOOL TESTS PASSED")
