"""In-memory shared state store for the Home Assistant system.

All agents can read and write to this store.
Pre-populated with default household context on startup.
"""

_DEFAULTS = {
    "who_is_home": ["Alice"],
    "preferred_movie_brightness": 30,
    "preferred_wake_time": "07:00",
    "location": "Home",
}

_store: dict = {}


def _init_defaults() -> None:
    """Load default values into the store."""
    _store.update({k: v if not isinstance(v, list) else list(v) for k, v in _DEFAULTS.items()})


def get_state(key: str):
    """Return the value for *key*, or ``None`` if it does not exist."""
    return _store.get(key)


def set_state(key: str, value) -> None:
    """Set *key* to *value* in the store."""
    _store[key] = value


def get_all_state() -> dict:
    """Return a shallow copy of the entire store."""
    return dict(_store)


def reset_state() -> None:
    """Clear the store and reload defaults. Useful for tests."""
    _store.clear()
    _init_defaults()


# Populate defaults on first import.
_init_defaults()
