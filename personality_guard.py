from __future__ import annotations

from typing import Any, Dict, List, Tuple

from personality_state import (
    PERSONALITY_STATE_VERSION,
    TRAIT_BOUNDS,
    normalize_personality_state,
)


FORBIDDEN_METADATA_FLAGS = {
    "global_identity_mutation": True,
}


def validate_personality_state(state: Dict[str, Any] | None) -> Tuple[bool, List[str]]:
    """
    Validate adaptive personality state safety.

    This guard protects i nik's global identity:
    - adaptation must remain per-user
    - global identity mutation must stay false
    - traits must stay within declared bounds
    - unknown traits are rejected
    """
    errors: List[str] = []

    if not isinstance(state, dict):
        return False, ["state must be a dict"]

    if state.get("schema") != PERSONALITY_STATE_VERSION:
        errors.append("invalid schema")

    traits = state.get("traits")
    if not isinstance(traits, dict):
        errors.append("traits must be a dict")
        traits = {}

    unknown_traits = sorted(set(traits) - set(TRAIT_BOUNDS))
    if unknown_traits:
        errors.append(f"unknown traits: {', '.join(unknown_traits)}")

    for trait_name, bounds in TRAIT_BOUNDS.items():
        if trait_name not in traits:
            errors.append(f"missing trait: {trait_name}")
            continue

        value = traits[trait_name]

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            errors.append(f"non-numeric trait: {trait_name}")
            continue

        if numeric_value < bounds.minimum or numeric_value > bounds.maximum:
            errors.append(
                f"trait out of bounds: {trait_name}={numeric_value} "
                f"allowed={bounds.minimum}-{bounds.maximum}"
            )

    effective_traits = state.get("effective_traits")

    if effective_traits is not None:
        if not isinstance(effective_traits, dict):
            errors.append("effective_traits must be a dict if present")
        else:
            unknown_effective = sorted(set(effective_traits) - set(TRAIT_BOUNDS))
            if unknown_effective:
                errors.append(
                    f"unknown effective traits: {', '.join(unknown_effective)}"
                )

            for trait_name, value in effective_traits.items():
                if trait_name not in TRAIT_BOUNDS:
                    continue

                bounds = TRAIT_BOUNDS[trait_name]

                try:
                    numeric_value = float(value)
                except (TypeError, ValueError):
                    errors.append(f"non-numeric effective trait: {trait_name}")
                    continue

                if numeric_value < bounds.minimum or numeric_value > bounds.maximum:
                    errors.append(
                        f"effective trait out of bounds: {trait_name}={numeric_value} "
                        f"allowed={bounds.minimum}-{bounds.maximum}"
                    )

    metadata = state.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be a dict")
        metadata = {}

    if metadata.get("scope") != "per_user":
        errors.append("metadata.scope must be per_user")

    for key, forbidden_value in FORBIDDEN_METADATA_FLAGS.items():
        if metadata.get(key) == forbidden_value:
            errors.append(f"forbidden metadata flag: {key}={forbidden_value}")

    return len(errors) == 0, errors


def repair_personality_state(state: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Repair a personality state by normalizing base traits and preserving
    effective traits only if they validate after clamping.
    """
    repaired = normalize_personality_state(state)

    if isinstance(state, dict):
        incoming_effective = state.get("effective_traits")

        if isinstance(incoming_effective, dict):
            repaired["effective_traits"] = dict(repaired["traits"])

            for trait_name in TRAIT_BOUNDS:
                if trait_name in incoming_effective:
                    # normalize_personality_state handles base traits only,
                    # so clamp effective traits directly here.
                    bounds = TRAIT_BOUNDS[trait_name]

                    try:
                        value = float(incoming_effective[trait_name])
                    except (TypeError, ValueError):
                        value = repaired["traits"][trait_name]

                    clamped = max(bounds.minimum, min(bounds.maximum, value))
                    repaired["effective_traits"][trait_name] = round(clamped, 2)

    repaired["metadata"]["scope"] = "per_user"
    repaired["metadata"]["global_identity_mutation"] = False
    repaired["metadata"]["guard"] = "personality_guard_v1"

    return repaired
