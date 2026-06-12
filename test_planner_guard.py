from planner_guard import normalize_plan


valid = normalize_plan({
    "goal": "points_lookup",
    "tool": "get_user_state",
    "arguments": {},
})
assert valid["ok"] is True
assert valid["tool"] == "get_user_state"

bad_type = normalize_plan(None)
assert bad_type["ok"] is False
assert bad_type["tool"] is None

bad_tool = normalize_plan({
    "goal": "bad",
    "tool": "delete_everything",
    "arguments": {},
})
assert bad_tool["ok"] is False
assert bad_tool["tool"] is None

bad_args = normalize_plan({
    "goal": "points_lookup",
    "tool": "get_user_state",
    "arguments": "not_dict",
})
assert bad_args["ok"] is True
assert bad_args["arguments"] == {}

print("PLANNER GUARD TESTS PASSED")
