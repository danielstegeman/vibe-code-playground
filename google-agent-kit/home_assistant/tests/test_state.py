"""Tests for the shared state store."""

import pytest

from home_assistant.state.store import (
    get_state,
    set_state,
    get_all_state,
    reset_state,
)


@pytest.fixture(autouse=True)
def _clean_state():
    """Reset the store before every test."""
    reset_state()


def test_defaults_present():
    assert get_state("who_is_home") == ["Alice"]
    assert get_state("preferred_movie_brightness") == 30
    assert get_state("preferred_wake_time") == "07:00"
    assert get_state("location") == "Home"


def test_get_missing_key_returns_none():
    assert get_state("nonexistent") is None


def test_set_and_get():
    set_state("color", "blue")
    assert get_state("color") == "blue"


def test_overwrite():
    set_state("location", "Office")
    assert get_state("location") == "Office"


def test_get_all_state_returns_copy():
    state = get_all_state()
    state["location"] = "Mars"
    assert get_state("location") == "Home"


def test_reset_restores_defaults():
    set_state("location", "Moon")
    reset_state()
    assert get_state("location") == "Home"
