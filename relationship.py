_NEGATIVE_WORDS = {
    "เกลียด", "น่าเบื่อ", "ห่วย", "แย่", "ไม่อยาก", "ทำไม",
    "ไม่ได้เลย", "ไร้สาระ", "เหนื่อย", "เซ็ง", "พูดได้แล้ว",
}

_EMOTIONAL_WORDS = {
    "เศร้า", "เหงา", "เหนื่อย", "ไม่ไหว", "พัง", "ร้องไห้",
    "กลัว", "กังวล", "เครียด", "เสียใจ", "น้อยใจ", "โดดเดี่ยว",
    "ไม่มีใครเข้าใจ", "หนัก", "แย่มาก",
}

_PERSONAL_DISCLOSURE_WORDS = {
    "ฉันชอบ", "ฉันไม่ชอบ", "ฉันกลัว", "ฉันอยาก", "ฉันรู้สึก",
    "ฉันเคย", "ฉันเป็น", "ฉันเรียน", "ฉันทำงาน", "ครอบครัว",
    "เพื่อน", "แฟน", "ชีวิต", "ความทรงจำ",
}

_REFLECTION_WORDS = {
    "เพราะ", "รู้สึกว่า", "คิดว่า", "หมายความว่า", "จริง ๆ",
    "บางที", "เหมือนว่า", "ฉันสงสัย", "ทำไมฉัน",
}

_PLAYFUL_WORDS = {
    "555", "ฮ่า", "ขำ", "แซว", "กวน", "น่ารัก", "แปลกดี",
}


def create_relationship_state():
    state = {
        "trust": 0,
        "familiarity": 0,
        "curiosity": 0,
        "attachment": 0,
    }
    return enrich_relationship_state(state)


def _clamp(value, low=0, high=100):
    return max(low, min(high, int(value)))


def _contains_any(text, words):
    return any(word in text for word in words)


def get_relationship_score(relationship_state):
    if relationship_state is None:
        relationship_state = create_relationship_state()

    trust = relationship_state.get("trust", 0)
    familiarity = relationship_state.get("familiarity", 0)
    curiosity = relationship_state.get("curiosity", 0)
    attachment = relationship_state.get("attachment", 0)

    return _clamp(
        (trust * 0.30)
        + (familiarity * 0.30)
        + (curiosity * 0.20)
        + (attachment * 0.20)
    )


def get_relationship_stage(score):
    score = _clamp(score)

    if score < 35:
        return "Observer"
    if score < 75:
        return "Gremlin"
    return "Treasure"


def enrich_relationship_state(relationship_state):
    if relationship_state is None:
        relationship_state = {}

    relationship_state["trust"] = _clamp(relationship_state.get("trust", 0))
    relationship_state["familiarity"] = _clamp(relationship_state.get("familiarity", 0))
    relationship_state["curiosity"] = _clamp(relationship_state.get("curiosity", 0))
    relationship_state["attachment"] = _clamp(relationship_state.get("attachment", 0))

    score = get_relationship_score(relationship_state)
    relationship_state["relationship_score"] = score
    relationship_state["relationship_stage"] = get_relationship_stage(score)

    return relationship_state


def update_relationship_state(user_message, relationship_state):
    if relationship_state is None:
        relationship_state = create_relationship_state()

    relationship_state = enrich_relationship_state(relationship_state)

    text = (user_message or "").strip()
    lowered = text.lower()

    if not text:
        return relationship_state

    trust_delta = 0
    familiarity_delta = 0
    curiosity_delta = 0
    attachment_delta = 0

    message_length = len(text)

    familiarity_delta += 1

    if _contains_any(text, _PERSONAL_DISCLOSURE_WORDS):
        trust_delta += 3
        familiarity_delta += 2
        curiosity_delta += 1
        attachment_delta += 1

    if _contains_any(text, _EMOTIONAL_WORDS):
        trust_delta += 4
        curiosity_delta += 1
        attachment_delta += 2

    if _contains_any(text, _REFLECTION_WORDS):
        curiosity_delta += 3

    if message_length >= 80:
        curiosity_delta += 2
        familiarity_delta += 1
        attachment_delta += 1
    elif message_length >= 40:
        curiosity_delta += 1

    if _contains_any(lowered, _PLAYFUL_WORDS):
        familiarity_delta += 2
        attachment_delta += 1

    if _contains_any(text, _NEGATIVE_WORDS):
        trust_delta -= 2
        familiarity_delta -= 1

    relationship_state["trust"] = _clamp(
        relationship_state.get("trust", 0) + trust_delta
    )
    relationship_state["familiarity"] = _clamp(
        relationship_state.get("familiarity", 0) + familiarity_delta
    )
    relationship_state["curiosity"] = _clamp(
        relationship_state.get("curiosity", 0) + curiosity_delta
    )
    relationship_state["attachment"] = _clamp(
        relationship_state.get("attachment", 0) + attachment_delta
    )

    return enrich_relationship_state(relationship_state)


def apply_relationship_decay(relationship_state, days_inactive):
    relationship_state = enrich_relationship_state(relationship_state)

    try:
        days = int(days_inactive or 0)
    except (TypeError, ValueError):
        days = 0

    if days <= 7:
        return relationship_state

    decay_units = days // 7

    familiarity_decay = min(20, decay_units * 2)
    curiosity_decay = min(15, decay_units * 2)
    attachment_decay = min(10, decay_units)

    relationship_state["familiarity"] = _clamp(
        relationship_state.get("familiarity", 0) - familiarity_decay
    )
    relationship_state["curiosity"] = _clamp(
        relationship_state.get("curiosity", 0) - curiosity_decay
    )
    relationship_state["attachment"] = _clamp(
        relationship_state.get("attachment", 0) - attachment_decay
    )

    return enrich_relationship_state(relationship_state)


def describe_relationship_state(relationship_state):
    relationship_state = enrich_relationship_state(relationship_state)

    trust = relationship_state.get("trust", 0)
    familiarity = relationship_state.get("familiarity", 0)
    curiosity = relationship_state.get("curiosity", 0)
    attachment = relationship_state.get("attachment", 0)
    relationship_score = relationship_state.get("relationship_score", 0)
    relationship_stage = relationship_state.get("relationship_stage", "Observer")

    return (
        "Relationship State:\n"
        f"- Trust: {trust}\n"
        f"- Familiarity: {familiarity}\n"
        f"- Curiosity: {curiosity}\n"
        f"- Attachment: {attachment}\n"
        f"- Relationship Score: {relationship_score}\n"
        f"- Relationship Stage: {relationship_stage}\n\n"
        "Interpretation:\n"
        "- Trust = ผู้ใช้เปิดใจหรือเล่าเรื่องส่วนตัวมากแค่ไหน\n"
        "- Familiarity = คุยกันบ่อยและคุ้นกันแค่ไหน\n"
        "- Curiosity = i nik สนใจแพตเทิร์นของผู้ใช้มากแค่ไหน\n"
        "- Attachment = ระดับความผูกพันเชิงตัวละคร ไม่ใช่ความโรแมนติก"
    )