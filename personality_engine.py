from __future__ import annotations

from typing import Any, Dict

from personality_state import (
    TRAIT_BOUNDS,
    create_personality_state,
    normalize_personality_state,
    clamp_trait,
)


EMOTIONAL_WORDS = [
    "เศร้า", "เหนื่อย", "ร้องไห้", "ไม่ไหว", "พัง", "แย่", "ท้อ",
]

PHILOSOPHY_WORDS = [
    "ชีวิต", "ความหมาย", "ทำไม", "จักรวาล", "มนุษย์", "ความทรงจำ",
]

MEMORY_WORDS = [
    "จำได้ไหม", "จำได้มั้ย", "จำ", "เคยบอก", "ความทรงจำ",
]

DIRECT_WORDS = [
    "สรุป", "ตรงๆ", "ตรง ๆ", "เอาสั้นๆ", "เอาสั้น ๆ", "ไม่ต้องอ้อม",
]


def _add(traits: Dict[str, float], name: str, delta: float) -> None:
    traits[name] = clamp_trait(name, traits.get(name, 0.0) + delta)


def _text_contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def derive_personality_state(
    base_state: Dict[str, Any] | None = None,
    relationship_state: Dict[str, Any] | None = None,
    user_profile: Dict[str, Any] | None = None,
    user_message: str = "",
) -> Dict[str, Any]:
    """
    Build a bounded per-user adaptive personality state.

    This function does not mutate global character identity.
    It only adjusts trait intensity within hard caps.
    """
    state = normalize_personality_state(base_state or create_personality_state())
    traits = dict(state["traits"])

    relationship_state = relationship_state or {}
    user_profile = user_profile or {}
    text = (user_message or "").strip()

    trust = int(relationship_state.get("trust", 0) or 0)
    familiarity = int(relationship_state.get("familiarity", 0) or 0)
    curiosity_score = int(relationship_state.get("curiosity", 0) or 0)
    attachment = int(relationship_state.get("attachment", 0) or 0)
    stage = relationship_state.get("relationship_stage", "")

    if trust >= 70:
        _add(traits, "warmth", 0.10)
    elif trust >= 40:
        _add(traits, "warmth", 0.05)

    if familiarity >= 70:
        _add(traits, "playfulness", 0.10)
        _add(traits, "formality", -0.10)
    elif familiarity >= 40:
        _add(traits, "playfulness", 0.05)
        _add(traits, "formality", -0.05)

    if curiosity_score >= 70:
        _add(traits, "curiosity", 0.10)
        _add(traits, "philosophy", 0.10)
    elif curiosity_score >= 40:
        _add(traits, "curiosity", 0.05)
        _add(traits, "philosophy", 0.05)

    if attachment >= 60:
        _add(traits, "memory_callback", 0.05)

    if stage == "Treasure":
        _add(traits, "memory_callback", 0.10)
        _add(traits, "warmth", 0.05)

    conversation_style = user_profile.get("conversation_style")
    recent_mood = user_profile.get("recent_mood")
    total_visits = int(user_profile.get("total_visits", 0) or 0)

    if conversation_style == "long-form":
        _add(traits, "philosophy", 0.05)

    if conversation_style in {"short", "direct", "concise"}:
        _add(traits, "directness", 0.05)

    if total_visits >= 10:
        _add(traits, "formality", -0.05)
        _add(traits, "memory_callback", 0.05)

    temporary_modifiers = {}

    if recent_mood in {"sad", "tired", "stressed"} or _text_contains_any(text, EMOTIONAL_WORDS):
        temporary_modifiers["warmth"] = 0.10
        temporary_modifiers["playfulness"] = -0.10

    if _text_contains_any(text, DIRECT_WORDS):
        temporary_modifiers["directness"] = temporary_modifiers.get("directness", 0.0) + 0.10

    if _text_contains_any(text, PHILOSOPHY_WORDS):
        temporary_modifiers["philosophy"] = temporary_modifiers.get("philosophy", 0.0) + 0.10

    if _text_contains_any(text, MEMORY_WORDS):
        temporary_modifiers["memory_callback"] = temporary_modifiers.get("memory_callback", 0.0) + 0.10

    effective_traits = dict(traits)

    for trait_name, delta in temporary_modifiers.items():
        if trait_name in TRAIT_BOUNDS:
            _add(effective_traits, trait_name, delta)

    return {
        "schema": state["schema"],
        "traits": traits,
        "effective_traits": effective_traits,
        "temporary_modifiers": temporary_modifiers,
        "metadata": {
            **state["metadata"],
            "scope": "per_user",
            "global_identity_mutation": False,
            "engine": "personality_engine_v1",
        },
    }
