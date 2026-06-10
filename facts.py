import re
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record_history(facts: dict, key: str, value: str) -> None:
    hist = facts.setdefault("_history", {})
    entries = hist.setdefault(key, [])
    entries.append({"value": value, "ts": _now_iso()})
    hist[key] = entries[-5:]


def clean_value(value):
    value = value.strip()

    endings = [
        "นะ", "น้า", "จ้า", "จ่ะ", "ค่ะ", "ครับ", "คับ",
        "อะ", "อ่ะ", "เว้ย", "นะคะ", "นะครับ"
    ]

    for ending in endings:
        if value.endswith(ending):
            value = value[: -len(ending)]

    value = value.strip()
    value = value.strip(" .,!?:;\"'“”‘’()[]{}")
    return value.strip()


def extract_facts(user_message, facts):
    text = user_message.strip()

    name_patterns = [
        r"ฉันชื่อ\s*([^\n,.!?]+)",
        r"เราชื่อ\s*([^\n,.!?]+)",
        r"ชื่อฉันคือ\s*([^\n,.!?]+)",
        r"ชื่อของฉันคือ\s*([^\n,.!?]+)",
        r"เรียกฉันว่า\s*([^\n,.!?]+)",
        r"เรียกเราว่า\s*([^\n,.!?]+)",
        r"ฉันคือ\s*([^\n,.!?]+)",
        r"เราคือ\s*([^\n,.!?]+)",
    ]

    for pattern in name_patterns:
        match = re.search(pattern, text)

        if not match:
            continue

        name = clean_value(match.group(1))

        blocked_words = {
            "อะไร",
            "ไร",
            "ใคร",
            "ไหม",
            "มั้ย",
            "หรือเปล่า",
            "ของฉัน",
            "ของเรา",
        }

        if (
            name
            and len(name) <= 30
            and name not in blocked_words
        ):
            _record_history(facts, "name", name)
            facts["name"] = name

    like_patterns = [
        r"ฉันชอบ\s*([^\n,.!?]+)",
        r"เราชอบ\s*([^\n,.!?]+)",
        r"ของโปรดฉันคือ\s*([^\n,.!?]+)",
        r"ของโปรดของฉันคือ\s*([^\n,.!?]+)",
    ]

    blocked_like_values = {
        "อะไร",
        "ไร",
        "อะไรนะ",
        "อะไรหรอ",
        "อะไรเหรอ",
        "ไหม",
        "มั้ย",
        "หรือเปล่า",
        "อะไรครับ",
        "อะไรคะ",
    }

    for pattern in like_patterns:
        match = re.search(pattern, text)

        if not match:
            continue

        liked = clean_value(match.group(1))

        if (
            liked
            and len(liked) <= 80
            and liked not in blocked_like_values
        ):
            _record_history(facts, "likes", liked)
            facts["likes"] = liked

    return facts


def is_name_question(user_message):
    text = user_message.strip().replace("?", "").replace("มั้ย", "ไหม")

    name_questions = [
        "ฉันชื่ออะไร",
        "เราชื่ออะไร",
        "ฉันชื่อไร",
        "เราชื่อไร",
        "จำชื่อฉันได้ไหม",
        "จำชื่อเราได้ไหม",
        "รู้ไหมฉันชื่ออะไร",
        "รู้ไหมเราชื่ออะไร",
        "ชื่อฉันคืออะไร",
        "ชื่อของฉันคืออะไร",
        "ชื่อเราอะไร",
        "ชื่อฉันอะไร",
    ]

    return any(question in text for question in name_questions)


def is_like_question(user_message):
    text = user_message.strip()
    text = text.replace("?", "")
    text = text.replace("มั้ย", "ไหม")

    like_questions = [
        "ฉันชอบอะไร",
        "เราชอบอะไร",
        "ฉันชอบไร",
        "เราชอบไร",
        "จำได้ไหมว่าฉันชอบอะไร",
        "จำได้ไหมว่าเราชอบอะไร",
        "ฉันชอบอะไรนะ",
        "เราชอบอะไรนะ",
    ]

    return any(question in text for question in like_questions)


def answer_from_facts(user_message, facts):

    if is_name_question(user_message):
        name = facts.get("name")

        if name:
            return (
                f"เธอชื่อ {name} ไง "
                "มนุษย์จำชื่อตัวเองไม่ไหวแล้วเหรอ "
                "หรือกำลังทดสอบ pixie ตัวเล็ก ๆ อยู่กันแน่"
            )

        return (
            "ฉันยังไม่รู้ชื่อเธอนะ "
            "ลองบอกฉันก่อนว่า 'ฉันชื่อ...' "
            "แล้วฉันจะพยายามจำให้ดี"
        )

    if is_like_question(user_message):
        liked = facts.get("likes")

        if liked:
            return f"เท่าที่ฉันจำได้ เธอชอบ {liked}"

        return "ฉันยังไม่รู้เลยว่าเธอชอบอะไร ลองบอกฉันก่อนสิ"

    return None