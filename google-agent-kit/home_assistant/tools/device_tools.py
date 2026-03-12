"""Mock tools for smart-home device control."""

_DEVICE_DB = {
    "lights_living_room": {
        "device_id": "lights_living_room",
        "state": "on",
        "brightness": 80,
        "locked": None,
    },
    "lights_kitchen": {
        "device_id": "lights_kitchen",
        "state": "on",
        "brightness": 100,
        "locked": None,
    },
    "lock_front_door": {
        "device_id": "lock_front_door",
        "state": "locked",
        "brightness": None,
        "locked": True,
    },
    "thermostat_main": {
        "device_id": "thermostat_main",
        "state": "on",
        "brightness": None,
        "locked": None,
        "temperature": 21,
    },
}


def get_device_state(device_id: str) -> dict:
    """Return the current state of a device.

    Args:
        device_id: Identifier for the device (e.g. ``lights_living_room``).

    Returns:
        A dict with at least ``device_id``, ``state``, ``brightness`` and ``locked``.
    """
    if device_id in _DEVICE_DB:
        return dict(_DEVICE_DB[device_id])
    return {
        "device_id": device_id,
        "state": "unknown",
        "brightness": None,
        "locked": None,
    }


def set_device_state(device_id: str, state: dict) -> dict:
    """Update the state of a device.

    Args:
        device_id: Identifier for the device.
        state: A dict of properties to update (e.g. ``{"brightness": 30}``).

    Returns:
        A dict confirming the update.
    """
    return {
        "success": True,
        "device_id": device_id,
        "updated": state,
    }
