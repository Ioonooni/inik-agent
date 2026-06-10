from agent_tools import list_available_tools


def build_plan(user_message: str, session_state):
    text = user_message.lower()

    if any(word in text for word in ["ชื่ออะไร", "ชื่อว่า", "ชื่อฉัน"]):
        return {
            "goal": "memory_lookup",
            "tool": "check_memory",
            "arguments": {"key": "name"}
        }

    if any(word in text for word in ["ชอบอะไร", "ชอบอะไรบ้าง"]):
        return {
            "goal": "memory_lookup",
            "tool": "check_memory",
            "arguments": {"key": "likes"}
        }

    if any(word in text for word in ["จำได้ไหม", "จำอะไรได้"]):
        return {
            "goal": "memory_lookup",
            "tool": "check_memory",
            "arguments": {}
        }

    if any(word in text for word in [
        "คะแนน",
        "แต้ม",
        "point",
        "points"
    ]):
        return {
            "goal": "points_lookup",
            "tool": "get_user_state",
            "arguments": {}
        }

    if any(word in text for word in [
        "inventory",
        "ไอเท็ม",
        "ของใน inventory",
        "ได้รับของ",
        "ได้รับอะไร",
        "ดูของ",
    ]):
        return {
            "goal": "inventory_lookup",
            "tool": "get_inventory",
            "arguments": {}
        }

    if any(word in text for word in [
        "สนิท",
        "ความสัมพันธ์",
        "trust",
        "curiosity"
    ]):
        return {
            "goal": "relationship_lookup",
            "tool": "get_relationship_state",
            "arguments": {}
        }

    return {
        "goal": "normal_chat",
        "tool": None,
        "arguments": {}
    }


def explain_plan(plan):
    if not plan:
        return "No plan"

    return (
        f"Goal={plan.get('goal')} | "
        f"Tool={plan.get('tool')}"
    )


if __name__ == "__main__":
    demo = build_plan(
        "ฉันชอบอะไร",
        {}
    )

    print(explain_plan(demo))