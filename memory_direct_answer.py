
import re
from typing import Any, Dict, Iterable, Optional


PET_QUESTION_WORDS = (
    "สัตว์เลี้ยงของฉันชื่ออะไร",
    "สัตว์เลี้ยงฉันชื่ออะไร",
    "นกของฉันชื่ออะไร",
    "นกฉันชื่ออะไร",
)

NAME_QUESTION_WORDS = (
    "ฉันชื่ออะไร",
    "ชื่อฉันคืออะไร",
    "ชื่อของฉันคืออะไร",
)

LIKE_QUESTION_WORDS = (
    "ฉันชอบอะไร",
    "ฉันชอบอะไรบ้าง",
)


def _memory_texts(raw_memories: Iterable[Any]) -> list[str]:
    texts = []
    for item in raw_memories or []:
        if isinstance(item, dict):
            content = item.get("content") or item.get("memory") or item.get("text") or ""
        else:
            content = str(item)
        if content:
            texts.append(str(content))
    return texts


def _find_pet_name(texts: list[str]) -> Optional[str]:
    patterns = [
        r"ฉันมีนกชื่อ\s*([ก-๙A-Za-z0-9_\-]+)",
        r"นกชื่อ\s*([ก-๙A-Za-z0-9_\-]+)",
        r"สัตว์เลี้ยง(?:ของฉัน)?ชื่อ\s*([ก-๙A-Za-z0-9_\-]+)",
        r"ฉันมีสัตว์เลี้ยงชื่อ\s*([ก-๙A-Za-z0-9_\-]+)",
    ]

    for text in reversed(texts):
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()
    return None


def answer_direct_memory_recall(
    user_message: str,
    user_facts: Dict[str, Any] | None = None,
    raw_memories: Iterable[Any] | None = None,
) -> Optional[str]:
    text = (user_message or "").strip().lower()
    facts = user_facts or {}
    memories = _memory_texts(raw_memories or [])

    if any(q in text for q in PET_QUESTION_WORDS) or ("สัตว์เลี้ยง" in text and "ชื่อ" in text):
        pet = facts.get("pet_name") or facts.get("pet") or _find_pet_name(memories)
        if pet:
            return f"เท่าที่ฉันจำได้ สัตว์เลี้ยงของเธอชื่อ {pet}"

    if any(q in text for q in NAME_QUESTION_WORDS):
        name = facts.get("name")
        if name:
            return f"เธอชื่อ {name} ไง"

    if any(q in text for q in LIKE_QUESTION_WORDS):
        likes = facts.get("likes")
        if likes:
            return f"เท่าที่ฉันจำได้ เธอชอบ {likes}"

    return None
