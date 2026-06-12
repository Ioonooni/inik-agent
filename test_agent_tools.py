from agent_tools import run_tool


class Session(dict):
    pass


def test_unknown_tool_returns_error():
    session = Session()
    result = run_tool("not_a_real_tool", session, {})
    assert result["ok"] is False
    assert "Unknown tool" in result["error"]


def test_grant_points_invalid_amount_falls_back_to_one():
    session = Session(points=0, inventory=[])
    result = run_tool("grant_points", session, {"amount": "abc"})
    assert result["ok"] is True
    assert session["points"] == 1


test_unknown_tool_returns_error()
test_grant_points_invalid_amount_falls_back_to_one()

print("AGENT TOOLS TESTS PASSED")
