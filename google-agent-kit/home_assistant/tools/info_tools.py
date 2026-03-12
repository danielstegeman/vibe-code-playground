"""Mock tools for weather and shopping-list queries."""

from ..state.store import get_state, set_state

_WEATHER_DB = {
    "Home": {
        "location": "Home",
        "condition": "clear",
        "temp_c": 14,
        "sunset": "18:40",
    },
    "Amsterdam": {
        "location": "Amsterdam",
        "condition": "cloudy",
        "temp_c": 11,
        "sunset": "18:35",
    },
}


def get_weather(location: str) -> dict:
    """Return the current weather for a location.

    Args:
        location: Name of the location (e.g. ``Home``).

    Returns:
        A dict with ``location``, ``condition``, ``temp_c`` and ``sunset``.
    """
    if location in _WEATHER_DB:
        return dict(_WEATHER_DB[location])
    return {
        "location": location,
        "condition": "unknown",
        "temp_c": None,
        "sunset": None,
    }


def get_shopping_list() -> dict:
    """Return the current shopping list.

    Returns:
        A dict with an ``items`` list.
    """
    items = get_state("shopping_list")
    if items is None:
        items = ["milk", "bread", "eggs"]
        set_state("shopping_list", list(items))
    return {"items": list(items)}


def add_to_shopping_list(item: str) -> dict:
    """Add an item to the shopping list.

    Args:
        item: The item to add.

    Returns:
        A dict confirming the addition and showing the updated list.
    """
    items = get_state("shopping_list")
    if items is None:
        items = ["milk", "bread", "eggs"]
    items.append(item)
    set_state("shopping_list", list(items))
    return {"success": True, "item": item, "list": list(items)}
