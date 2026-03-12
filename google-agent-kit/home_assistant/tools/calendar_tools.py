"""Mock tools for calendar and scheduling."""

_TEST_DATE = "2025-03-15"
_TEST_EVENT = {
    "event_id": "evt001",
    "title": "Dinner with Bob",
    "date": _TEST_DATE,
    "time": "19:00",
}


def get_calendar_events(date: str) -> dict:
    """Return calendar events for a given date.

    Args:
        date: ISO-8601 date string (e.g. ``2025-03-12``).

    Returns:
        A dict with ``date`` and a list of ``events``.
    """
    if date == _TEST_DATE:
        return {"date": date, "events": [_TEST_EVENT]}
    return {"date": date, "events": []}


def create_calendar_event(title: str, date: str, time: str) -> dict:
    """Create a new calendar event.

    Args:
        title: Title of the event.
        date: ISO-8601 date string.
        time: Time in HH:MM format.

    Returns:
        A dict confirming the created event.
    """
    return {
        "success": True,
        "event_id": "abc123",
        "title": title,
        "date": date,
        "time": time,
    }
