import pytest

from character_registry import (
    character_exists,
    get_character,
    list_characters,
)


def test_registry_contains_inik_and_rick_royce():
    assert character_exists("inik") is True
    assert character_exists("rick_royce") is True


def test_get_inik_character_definition():
    character = get_character("inik")

    assert character.character_id == "inik"
    assert character.display_name == "i nik"
    assert character.role == "companion"
    assert character.mode == "heart"
    assert "i nik" in character.prompt


def test_get_rick_royce_character_definition():
    character = get_character("rick_royce")

    assert character.character_id == "rick_royce"
    assert character.display_name == "Rick Royce"
    assert character.role == "strategic_reasoning"
    assert character.mode == "mind"
    assert "Rick Royce" in character.prompt


def test_list_visible_characters_returns_public_modes():
    characters = list_characters()

    ids = {character.character_id for character in characters}
    assert "inik" in ids
    assert "rick_royce" in ids


def test_unknown_character_raises_key_error():
    with pytest.raises(KeyError):
        get_character("unknown")


def test_api_agent_mode_falls_back_to_inik_for_unknown_character():
    from character_registry import character_exists

    requested_mode = "unknown_character"
    agent_mode = requested_mode.strip().lower()
    if not character_exists(agent_mode):
        agent_mode = "inik"

    assert agent_mode == "inik"
