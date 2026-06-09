def create_relationship_state():
    return {
        "trust": 0,
        "familiarity": 0,
        "curiosity": 0
    }


def update_relationship_state(user_message, relationship_state):
    message_length = len(user_message)

    # Familiarity: ยิ่งคุยบ่อย ระบบยิ่งคุ้น
    relationship_state["familiarity"] += 1

    # Curiosity: ถ้าผู้ใช้เล่าเยอะหรือถามอะไรลึก ระบบสนใจมากขึ้น
    if message_length >= 40:
        relationship_state["curiosity"] += 2

    if any(word in user_message for word in ["ทำไม", "ชีวิต", "ความหมาย", "มนุษย์", "รู้สึก"]):
        relationship_state["curiosity"] += 2

    # Trust: ถ้าผู้ใช้เล่าเรื่องส่วนตัวหรืออารมณ์ ระบบถือว่าไว้ใจมากขึ้น
    if any(word in user_message for word in ["ฉันรู้สึก", "เหนื่อย", "เศร้า", "กลัว", "ไม่ไหว", "เสียใจ"]):
        relationship_state["trust"] += 3

    # จำกัดคะแนนไม่ให้เกิน 100
    relationship_state["trust"] = min(100, relationship_state["trust"])
    relationship_state["familiarity"] = min(100, relationship_state["familiarity"])
    relationship_state["curiosity"] = min(100, relationship_state["curiosity"])

    return relationship_state


def describe_relationship_state(relationship_state):
    trust = relationship_state["trust"]
    familiarity = relationship_state["familiarity"]
    curiosity = relationship_state["curiosity"]

    return f"""
Relationship State:
- Trust: {trust}
- Familiarity: {familiarity}
- Curiosity: {curiosity}

Interpretation:
- Trust = ผู้ใช้เปิดใจหรือเล่าเรื่องส่วนตัวมากแค่ไหน
- Familiarity = คุยกันบ่อยและคุ้นกันแค่ไหน
- Curiosity = i nik สนใจแพทเทิร์นของผู้ใช้มากแค่ไหน
"""