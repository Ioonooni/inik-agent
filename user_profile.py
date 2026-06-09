from datetime import datetime


def create_user_profile():
    return {
        "recent_mood": "neutral",
        "conversation_style": "unknown",
        "recurring_topics": [],
        "memorable_events": [],
        "total_messages": 0,
        "total_visits": 0,
        "last_interaction_date": None
    }


def normalize_user_profile(user_profile):
    default_profile = create_user_profile()

    if not user_profile:
        return default_profile

    for key, value in default_profile.items():
        if key not in user_profile:
            user_profile[key] = value

    return user_profile


def register_visit(user_profile):
    user_profile = normalize_user_profile(user_profile)
    user_profile["total_visits"] += 1
    return user_profile


def detect_recent_mood(user_message):
    text = user_message.strip()

    tired_words = ["เหนื่อย", "หมดแรง", "ล้า", "ไม่ไหว", "เพลีย"]
    sad_words = ["เศร้า", "เสียใจ", "ร้องไห้", "เจ็บ", "พัง"]
    anxious_words = ["กังวล", "กลัว", "เครียด", "ตื่นเต้น", "ไม่มั่นใจ"]
    happy_words = ["ดีใจ", "มีความสุข", "สนุก", "ตื่นเต้นดี", "แฮปปี้"]

    if any(word in text for word in tired_words):
        return "tired"

    if any(word in text for word in sad_words):
        return "sad"

    if any(word in text for word in anxious_words):
        return "anxious"

    if any(word in text for word in happy_words):
        return "happy"

    return "neutral"


def detect_conversation_style(user_message):
    text = user_message.strip()

    if len(text) >= 80:
        return "long-form"

    if any(word in text for word in ["ทำไม", "ความหมาย", "ชีวิต", "มนุษย์", "จักรวาล"]):
        return "philosophical"

    if any(word in text for word in ["555", "ขำ", "กวน", "แซว"]):
        return "playful"

    if any(word in text for word in ["เหนื่อย", "เศร้า", "ไม่ไหว", "เครียด"]):
        return "emotional"

    return "casual"


def detect_topics(user_message):
    text = user_message.strip()

    topic_keywords = {
        "memory": ["จำ", "ความทรงจำ", "ลืม"],
        "human": ["มนุษย์", "คน", "ชีวิต"],
        "emotion": ["รู้สึก", "เศร้า", "เหนื่อย", "ดีใจ", "กลัว", "เครียด"],
        "universe": ["จักรวาล", "ดาว", "โลก", "อวกาศ"],
        "identity": ["ตัวตน", "ฉันเป็น", "นิสัย", "บุคลิก"],
        "relationship": ["ความสัมพันธ์", "สนิท", "ไว้ใจ", "คิดถึง"],
        "reward": ["รางวัล", "แต้ม", "ของสะสม", "inventory"],
    }

    detected = []

    for topic, keywords in topic_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected.append(topic)

    return detected


def update_user_profile(user_message, user_profile):
    user_profile = normalize_user_profile(user_profile)

    recent_mood = detect_recent_mood(user_message)
    conversation_style = detect_conversation_style(user_message)
    detected_topics = detect_topics(user_message)

    user_profile["total_messages"] += 1
    user_profile["last_interaction_date"] = datetime.now().isoformat(timespec="seconds")

    if recent_mood != "neutral":
        user_profile["recent_mood"] = recent_mood

    if conversation_style != "casual":
        user_profile["conversation_style"] = conversation_style

    for topic in detected_topics:
        if topic not in user_profile["recurring_topics"]:
            user_profile["recurring_topics"].append(topic)

    user_profile["recurring_topics"] = user_profile["recurring_topics"][-10:]

    if len(user_message.strip()) >= 100:
        memorable_event = user_message.strip()

        if memorable_event not in user_profile["memorable_events"]:
            user_profile["memorable_events"].append(memorable_event)

        user_profile["memorable_events"] = user_profile["memorable_events"][-5:]

    return user_profile


def describe_user_profile(user_profile):
    user_profile = normalize_user_profile(user_profile)

    recent_mood = user_profile.get("recent_mood", "neutral")
    conversation_style = user_profile.get("conversation_style", "unknown")
    recurring_topics = user_profile.get("recurring_topics", [])
    memorable_events = user_profile.get("memorable_events", [])
    total_messages = user_profile.get("total_messages", 0)
    total_visits = user_profile.get("total_visits", 0)
    last_interaction_date = user_profile.get("last_interaction_date")

    return f"""
User Profile:
- Recent Mood: {recent_mood}
- Conversation Style: {conversation_style}
- Recurring Topics: {recurring_topics}
- Memorable Events Count: {len(memorable_events)}
- Total User Messages: {total_messages}
- Total Visits: {total_visits}
- Last Interaction Date: {last_interaction_date}
"""