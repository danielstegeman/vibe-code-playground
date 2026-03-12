"""Tests for mock tools."""

import pytest

from home_assistant.tools.device_tools import get_device_state, set_device_state
from home_assistant.tools.calendar_tools import get_calendar_events, create_calendar_event
from home_assistant.tools.info_tools import get_weather, get_shopping_list, add_to_shopping_list
from home_assistant.state.store import reset_state


@pytest.fixture(autouse=True)
def _clean_state():
    reset_state()


# -- Device tools --

class TestGetDeviceState:
    def test_known_device(self):
        result = get_device_state("lights_living_room")
        assert result["device_id"] == "lights_living_room"
        assert result["state"] == "on"
        assert result["brightness"] == 80

    def test_unknown_device(self):
        result = get_device_state("does_not_exist")
        assert result["state"] == "unknown"

    def test_lock_device(self):
        result = get_device_state("lock_front_door")
        assert result["locked"] is True


class TestSetDeviceState:
    def test_returns_success(self):
        result = set_device_state("lights_living_room", {"brightness": 30})
        assert result["success"] is True
        assert result["device_id"] == "lights_living_room"
        assert result["updated"] == {"brightness": 30}


# -- Calendar tools --

class TestGetCalendarEvents:
    def test_date_with_event(self):
        result = get_calendar_events("2025-03-15")
        assert len(result["events"]) == 1
        assert result["events"][0]["title"] == "Dinner with Bob"

    def test_date_without_events(self):
        result = get_calendar_events("2025-01-01")
        assert result["events"] == []


class TestCreateCalendarEvent:
    def test_creates_event(self):
        result = create_calendar_event("Movie Night", "2025-03-12", "20:00")
        assert result["success"] is True
        assert result["title"] == "Movie Night"
        assert result["time"] == "20:00"


# -- Info tools --

class TestGetWeather:
    def test_known_location(self):
        result = get_weather("Home")
        assert result["condition"] == "clear"
        assert result["temp_c"] == 14
        assert result["sunset"] == "18:40"

    def test_unknown_location(self):
        result = get_weather("Mars")
        assert result["condition"] == "unknown"


class TestGetShoppingList:
    def test_default_list(self):
        result = get_shopping_list()
        assert result["items"] == ["milk", "bread", "eggs"]


class TestAddToShoppingList:
    def test_add_item(self):
        result = add_to_shopping_list("butter")
        assert result["success"] is True
        assert result["item"] == "butter"
        assert "butter" in result["list"]

    def test_list_persists(self):
        add_to_shopping_list("butter")
        result = get_shopping_list()
        assert "butter" in result["items"]
