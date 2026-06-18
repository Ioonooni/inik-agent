from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict


PERSONALITY_STATE_VERSION = "adaptive_personality_v1"


@dataclass(frozen=True)
class PersonalityBounds:
    minimum: float
    maximum: float


TRAIT_BOUNDS: Dict[str, PersonalityBounds] = {
    "warmth": PersonalityBounds(0.0, 0.85),
    "playfulness": PersonalityBounds(0.0, 0.75),
    "curiosity": PersonalityBounds(0.0, 0.85),
    "directness": PersonalityBounds(0.0, 0.75),
    "philosophy": PersonalityBounds(0.0, 0.80),
    "initiative": PersonalityBounds(0.0, 0.60),
    "memory_callback": PersonalityBounds(0.0, 0.70),
    "formality": PersonalityBounds(0.0, 0.75),
}


DEFAULT_PERSONALITY_STATE: Dict[str, Any] = {
    "schema": PERSONALITY_STATE_VERSION,
    "traits": {
        "warmth": 0.50,
        "playfulness": 0.45,
        "curiosity": 0.60,
        "directness": 0.45,
        "philosophy": 0.55,
        "initiative": 0.25,
        "memory_callback": 0.30,
        "formality": 0.45,
    },
    "metadata": {
        "scope": "per_user",
        "global_identity_mutation": False,
    },
}


def clamp_trait(name: str, value: Any) -> float:
    bounds = TRAIT_BOUNDS[name]

    try:
        number = float(value)
    except (TypeError, ValueError):
        number = DEFAULT_PERSONALITY_STATE["traits"][name]

    clamped = max(bounds.minimum, min(bounds.maximum, number))
    return round(clamped, 2)


def create_personality_state() -> Dict[str, Any]:
    return {
        "schema": PERSONALITY_STATE_VERSION,
        "traits": dict(DEFAULT_PERSONALITY_STATE["traits"]),
        "metadata": dict(DEFAULT_PERSONALITY_STATE["metadata"]),
    }


def normalize_personality_state(state: Dict[str, Any] | None) -> Dict[str, Any]:
    normalized = create_personality_state()

    if not isinstance(state, dict):
        return normalized

    incoming_traits = state.get("traits") or {}

    if isinstance(incoming_traits, dict):
        for trait_name in TRAIT_BOUNDS:
            if trait_name in incoming_traits:
                normalized["traits"][trait_name] = clamp_trait(
                    trait_name,
                    incoming_traits[trait_name],
                )

    incoming_metadata = state.get("metadata") or {}

    if isinstance(incoming_metadata, dict):
        normalized["metadata"].update(incoming_metadata)

    normalized["schema"] = PERSONALITY_STATE_VERSION
    normalized["metadata"]["scope"] = "per_user"
    normalized["metadata"]["global_identity_mutation"] = False

    return normalized


def describe_personality_state(state: Dict[str, Any] | None) -> str:
    normalized = normalize_personality_state(state)
    traits = normalized["traits"]

    lines = [
        "Adaptive Personality State:",
        "- Scope: per-user adaptation",
        "- Global Identity Mutation: false",
    ]

    for trait_name in sorted(traits):
        lines.append(f"- {trait_name}: {traits[trait_name]:.2f}")

    return "\n".join(lines)
