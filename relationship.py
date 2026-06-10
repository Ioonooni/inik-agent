_NEGATIVE_WORDS = {
    "เกลียด", "น่าเบื่อ", "ห่วย", "โง่", "แย่",
    "ไม่อยาก", "หนีไป", "ไปได้เลย", "เลิกคุย",
    "น่ารำคาญ", "ไม่ชอบ", "เซ็ง", "หยุดได้แล้ว",
}


def create_relationship_state():
    return {
        "trust": 0,
        "familiarity": 0,
        "curiosity": 0,
    }


def update_relationship_state(user_message, relationship_state):
    text = user_message

    if any(word in text for word in _NEGATIVE_WORDS):
        relationship_state["trust"] = max(0, relationship_state["trust"] - 2)
        relationship_state["familiarity"] = max(0, relationship_state["familiarity"] - 1)
        return relationship_state

    message_length = len(user_message)

    relationship_state["familiarity"] = min(100, relationship_state["familiarity"] + 1)

    if message_length >= 40:
        relationship_state["curiosity"] = min(100, relationship_state["curiosity"] + 2)

    if any(word in text for word in ["ทำไม", "ชีวิต", "ความหมาย", "มนุษย์", "รู้สึก"]):
        relationship_state["curiosity"] = min(100, relationship_state["curiosity"] + 2)

    if any(word in text for word in ["ฉันรู้สึก", "เหนื่อย", "เศร้า", "กลัว", "ไม่ไหว", "เสียใจ"]):
        relationship_state["trust"] = min(100, relationship_state["trust"] + 3)

    return relationship_state


def describe_relationship_state(relationship_state):
    trust = relationship_state["trust"]
    familiarity = relationship_state["familiarity"]
    curiosity = relationship_state["curiosity"]

    return (
        "Relationship State:\n"
        f"- Trust: {trust}\n"
        f"- Familiarity: {familiarity}\n"
        f"- Curiosity: {curiosity}\n\n"
        "Interpretation:\n"
        "- Trust = ผู้ใช้เปิดใจหรือเล่าเรื่องส่วนตัวมากแค่ไหน\n"
        "- Familiarity = คุยกันบ่อยและคุ้นกันแค่ไหน\n"
        "- Curiosity = i nik สนใจแพทเทิร์นของผู้ใช้มากแค่ไหน"
    )
