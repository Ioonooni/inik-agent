from dataclasses import dataclass
from typing import Dict, List

from character import CHARACTER_BIBLE
from rick_prompt import RICK_ROYCE_SYSTEM_PROMPT


@dataclass(frozen=True)
class CharacterDefinition:
    character_id: str
    display_name: str
    role: str
    mode: str
    prompt: str
    visible_to_user: bool
    description: str


CHARACTER_REGISTRY: Dict[str, CharacterDefinition] = {
    "inik": CharacterDefinition(
        character_id="inik",
        display_name="i nik",
        role="companion",
        mode="heart",
        prompt=CHARACTER_BIBLE,
        visible_to_user=True,
        description="Emotional memory layer, relationship continuity, and character interaction.",
    ),
    "rick_royce": CharacterDefinition(
        character_id="rick_royce",
        display_name="Rick Royce",
        role="strategic_reasoning",
        mode="mind",
        prompt=RICK_ROYCE_SYSTEM_PROMPT,
        visible_to_user=True,
        description="Strategic reasoning layer for decisions, tradeoffs, risk, and capital allocation.",
    ),
}


def get_character(character_id: str) -> CharacterDefinition:
    key = (character_id or "").strip().lower()

    if key not in CHARACTER_REGISTRY:
        raise KeyError(f"unknown character_id: {character_id}")

    return CHARACTER_REGISTRY[key]


def list_characters(visible_only: bool = True) -> List[CharacterDefinition]:
    characters = list(CHARACTER_REGISTRY.values())

    if visible_only:
        return [character for character in characters if character.visible_to_user]

    return characters


def character_exists(character_id: str) -> bool:
    key = (character_id or "").strip().lower()
    return key in CHARACTER_REGISTRY
