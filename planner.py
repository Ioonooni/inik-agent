from agent_tools import list_available_tools


def build_plan(user_message: str, session_state):
    text = (user_message or "").lower().strip()

    memory_keywords = [
        "จำได้ไหม",
        "จำได้มั้ย",
        "จำอะไรได้",
        "ชอบอะไร",
        "ชื่ออะไร",
        "ฉันชื่อ",
        "เราชื่อ",
    ]

    user_state_keywords = [
        "สถานะของฉัน",
        "สถานะฉัน",
        "สถานะเรา",
        "สถานะของเรา",
        "สถานะตอนนี้",
        "stage",
        "สเตจ",
        "คะแนน",
        "แต้ม",
        "point",
        "points",
    ]

    inventory_keywords = [
        "ของรางวัล",
        "ของที่มี",
        "ของใน inventory",
        "inventory",
        "ไอเท็ม",
        "item",
        "items",
        "ได้รับอะไร",
        "มีของอะไร",
        "มีอะไรในคลัง",
    ]

    relationship_keywords = [
        "ความสัมพันธ์",
        "สนิท",
        "trust",
        "familiarity",
        "curiosity",
        "ความไว้ใจ",
        "ความคุ้นเคย",
    ]

    visit_keywords = [
        "มากี่ครั้ง",
        "คุยกี่ครั้ง",
        "แวะมากี่ครั้ง",
        "total visits",
        "total messages",
    ]

    if any(word in text for word in memory_keywords):
        return {
            "goal": "memory_lookup",
            "tool": "check_memory",
            "arguments": {}
        }

    if any(word in text for word in user_state_keywords):
        return {
            "goal": "user_state_lookup",
            "tool": "get_user_state",
            "arguments": {}
        }

    if any(word in text for word in inventory_keywords):
        return {
            "goal": "inventory_lookup",
            "tool": "get_inventory",
            "arguments": {}
        }

    if any(word in text for word in relationship_keywords):
        return {
            "goal": "relationship_lookup",
            "tool": "get_relationship_state",
            "arguments": {}
        }

    if any(word in text for word in visit_keywords):
        return {
            "goal": "visit_count_lookup",
            "tool": "get_visit_count",
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
    test_messages = [
        "สถานะของฉัน",
        "ฉันมีของรางวัลอะไรบ้าง",
        "ฉันชอบอะไร",
        "ความสัมพันธ์ตอนนี้เป็นไง",
        "ฉันคุยกี่ครั้งแล้ว",
    ]

    for message in test_messages:
        plan = build_plan(message, {})
        print(message, "=>", explain_plan(plan))