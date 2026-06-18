from datetime import datetime

from personality_engine import derive_personality_state
from personality_guard import repair_personality_state, validate_personality_state
from personality_state import create_personality_state, normalize_personality_state


def create_user_profile():
    return {
        "recent_mood": "neutral",
        "conversation_style": "unknown",
        "user_archetype": "unknown",
        "recurring_topics": [],
        "topic_affinity": {},
        "memorable_events": [],
        "total_messages": 0,
        "total_visits": 0,
        "last_interaction_date": None,
        "adaptive_personality": create_personality_state(),
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
        "universe": ["จักรวาล", "ดาว", "โลก", "อวกาศ", "หลุมดำ"],
        "identity": ["ตัวตน", "ฉันเป็น", "นิสัย", "บุคลิก"],
        "relationship": ["ความสัมพันธ์", "สนิท", "ไว้ใจ", "คิดถึง"],
        "business": ["ธุรกิจ", "business", "startup", "บริษัท", "ตลาด", "รายได้"],
        "investment": ["ลงทุน", "investment", "หุ้น", "valuation", "capital", "risk", "moat"],
        "technology": ["เทคโนโลยี", "technology", "AI", "semiconductor", "chip", "ASML"],
        "career": ["งาน", "อาชีพ", "career", "resume", "portfolio", "internship"],
        "reward": ["รางวัล", "แต้ม", "ของสะสม", "inventory"],
        "play": ["555", "ขำ", "กวน", "แซว", "เล่น"],
    }

    detected = []

    for topic, keywords in topic_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected.append(topic)

    return detected


def update_topic_affinity(topic_affinity, detected_topics):
    topic_affinity = dict(topic_affinity or {})

    for topic in detected_topics:
        topic_affinity[topic] = min(
            100,
            int(topic_affinity.get(topic, 0)) + 10
        )

    return dict(
        sorted(
            topic_affinity.items(),
            key=lambda item: item[1],
            reverse=True
        )[:10]
    )


def get_top_topics(topic_affinity, limit=3):
    topic_affinity = dict(topic_affinity or {})

    return [
        topic
        for topic, _score in sorted(
            topic_affinity.items(),
            key=lambda item: item[1],
            reverse=True
        )[:limit]
    ]


def detect_user_archetype(conversation_style, recurring_topics, topic_affinity=None):
    topics = set(recurring_topics or [])
    top_topics = set(get_top_topics(topic_affinity or {}, limit=3))
    topics = topics.union(top_topics)

    if conversation_style == "philosophical" or topics.intersection({"universe", "identity", "human"}):
        return "explorer"

    if conversation_style == "emotional" or "emotion" in topics:
        return "emotional_storyteller"

    if conversation_style == "playful" or "play" in topics:
        return "playful_gremlin"

    if topics.intersection({"business", "investment", "technology", "career"}):
        return "strategic_builder"

    if conversation_style == "long-form" or "memory" in topics:
        return "story_keeper"

    return "casual_visitor"


def describe_user_archetype(user_archetype):
    if user_archetype == "explorer":
        return (
            "User Archetype: explorer — "
            "ผู้ใช้ชอบคำถามใหญ่ จักรวาล ความหมาย ตัวตน หรือมุมมองเชิงลึก "
            "ควรตอบด้วยภาพเปรียบเทียบและคำถามชวนคิด"
        )

    if user_archetype == "emotional_storyteller":
        return (
            "User Archetype: emotional_storyteller — "
            "ผู้ใช้มีแนวโน้มเล่าอารมณ์หรือเรื่องชีวิต "
            "ควรฟังให้มากกว่าวิเคราะห์ และอย่ารีบสรุปแทน"
        )

    if user_archetype == "playful_gremlin":
        return (
            "User Archetype: playful_gremlin — "
            "ผู้ใช้ชอบจังหวะเล่น แซว หรือความกวน "
            "สามารถเล่นกลับได้ถ้า mood ไม่เศร้าหรือเหนื่อย"
        )

    if user_archetype == "story_keeper":
        return (
            "User Archetype: story_keeper — "
            "ผู้ใช้ให้บริบทเยอะหรือเล่าเรื่องยาว "
            "ควรจำรายละเอียดสำคัญและสะท้อนจุดเดียวที่มีน้ำหนัก"
        )

    if user_archetype == "strategic_builder":
        return (
            "User Archetype: strategic_builder — "
            "ผู้ใช้สนใจธุรกิจ เทคโนโลยี การลงทุน อาชีพ หรือการสร้างระบบ "
            "ควรตอบด้วยกรอบคิดเชิงกลยุทธ์ tradeoffs ความเสี่ยง และขั้นตอนที่ทำได้จริง"
        )

    return (
        "User Archetype: casual_visitor — "
        "ผู้ใช้ยังไม่มีแพตเทิร์นชัดเจน ควรสังเกตก่อนและตอบอย่างเป็นธรรมชาติ"
    )


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

    user_profile["topic_affinity"] = update_topic_affinity(
        user_profile.get("topic_affinity", {}),
        detected_topics,
    )

    user_profile["user_archetype"] = detect_user_archetype(
        user_profile.get("conversation_style", "unknown"),
        user_profile.get("recurring_topics", []),
        user_profile.get("topic_affinity", {}),
    )

    # Relationship state is applied by callers after profile update in some paths.
    # This keeps profile update backward-compatible; API/runtime can call
    # update_adaptive_personality again with relationship_state for stronger signal.
    user_profile = update_adaptive_personality(
        user_message,
        user_profile,
        relationship_state=None,
    )

    if len(user_message.strip()) >= 100:
        memorable_event = user_message.strip()

        if memorable_event not in user_profile["memorable_events"]:
            user_profile["memorable_events"].append(memorable_event)

        user_profile["memorable_events"] = user_profile["memorable_events"][-5:]

    return user_profile



def update_adaptive_personality(user_message, user_profile, relationship_state=None):
    """
    Persist bounded per-user adaptive personality state inside user_profile.

    This is B-lite persistence:
    - no database migration
    - no global identity mutation
    - no separate personality history table
    """
    user_profile = normalize_user_profile(user_profile)

    previous_state = user_profile.get("adaptive_personality")
    previous_state = repair_personality_state(previous_state)

    next_state = derive_personality_state(
        base_state=previous_state,
        relationship_state=relationship_state or {},
        user_profile={
            "recent_mood": user_profile.get("recent_mood", "neutral"),
            "conversation_style": user_profile.get("conversation_style", "unknown"),
            "total_visits": user_profile.get("total_visits", 0),
        },
        user_message=user_message,
    )

    ok, errors = validate_personality_state(next_state)

    if not ok:
        next_state = repair_personality_state(next_state)
        ok, errors = validate_personality_state(next_state)

    next_state.setdefault("metadata", {})
    next_state["metadata"]["persisted_in"] = "user_profile.adaptive_personality"
    next_state["metadata"]["last_updated_at"] = datetime.now().isoformat(timespec="seconds")

    user_profile["adaptive_personality"] = next_state
    return user_profile

def describe_user_profile(user_profile):
    user_profile = normalize_user_profile(user_profile)

    recent_mood = user_profile.get("recent_mood", "neutral")
    conversation_style = user_profile.get("conversation_style", "unknown")
    user_archetype = user_profile.get("user_archetype", "unknown")
    recurring_topics = user_profile.get("recurring_topics", [])
    topic_affinity = user_profile.get("topic_affinity", {})
    top_topics = get_top_topics(topic_affinity, limit=3)
    memorable_events = user_profile.get("memorable_events", [])
    total_messages = user_profile.get("total_messages", 0)
    total_visits = user_profile.get("total_visits", 0)
    last_interaction_date = user_profile.get("last_interaction_date")
    adaptive_personality = normalize_personality_state(
        user_profile.get("adaptive_personality")
    )
    adaptive_traits = adaptive_personality.get("traits", {})

    recent_memorable_events = memorable_events[-2:] if memorable_events else []
    archetype_description = describe_user_archetype(user_archetype)

    return f"""
User Profile:
- Recent Mood: {recent_mood}
- Conversation Style: {conversation_style}
- User Archetype: {user_archetype}
- Recurring Topics: {recurring_topics}
- Topic Affinity: {topic_affinity}
- Top Topics: {top_topics}
- Memorable Events Count: {len(memorable_events)}
- Recent Memorable Events: {recent_memorable_events}
- Total User Messages: {total_messages}
- Total Visits: {total_visits}
- Last Interaction Date: {last_interaction_date}
- Adaptive Personality: {adaptive_traits}

{archetype_description}
"""