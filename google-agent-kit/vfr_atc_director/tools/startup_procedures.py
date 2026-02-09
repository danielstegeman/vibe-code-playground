"""Startup and ground procedures tool for ATC simulation."""

from typing import Any
from google.adk.tools import ToolContext


def get_startup_clearance_procedure(
    tool_context: ToolContext,
    aircraft_callsign: str,
    aircraft_location: str = "ramp",
    altimeter_setting: str | None = None,
) -> dict[str, Any]:
    """Provide startup clearance procedure and phraseology.
    
    Use this tool when a pilot requests engine start/startup permission.
    Provides the correct ATC response format and required information.
    
    Args:
        tool_context: ADK tool context
        aircraft_callsign: Aircraft callsign (e.g., "N12345", "Skyhawk 345")
        aircraft_location: Where the aircraft is parked (e.g., "ramp", "gate 5", "transient parking")
        altimeter_setting: Current altimeter setting in inches Hg (e.g., "29.92", "30.15")
    
    Returns:
        Dictionary with startup clearance information and phraseology guidance
    """
    # Build standard startup clearance
    standard_phraseology = f"{aircraft_callsign}, startup approved"
    if altimeter_setting:
        standard_phraseology += f", altimeter {altimeter_setting}"
    
    result = {
        "procedure_type": "startup_clearance",
        "aircraft_callsign": aircraft_callsign,
        "aircraft_location": aircraft_location,
        "altimeter_setting": altimeter_setting,
        "standard_phraseology": standard_phraseology,
        "pilot_expected_readback": f"Startup approved, altimeter {altimeter_setting or '[value]'}, will advise ready to taxi, {aircraft_callsign}",
        "common_variations": [
            "If clearance delivery is separate: 'Startup approved, contact ground point niner when ready to taxi'",
            "If hold for IFR release: 'Startup approved, hold for IFR release, advise ready'",
            "If busy traffic: 'Startup approved, expect [delay] minute delay, advise ready to taxi'"
        ],
        "required_information": {
            "altimeter_setting": altimeter_setting or "Use current altimeter (typically 29.92 or local setting)",
            "atis_information": "Optional: ATIS letter if available (Alpha, Bravo, etc.)",
            "taxi_instructions": "Will be provided after pilot advises ready"
        },
        "safety_critical_items": [
            "Always provide current altimeter setting",
            "Confirm pilot has current ATIS if available",
            "Advise pilot to contact ground when ready to taxi"
        ]
    }
    
    return result


def get_taxi_clearance_procedure(
    tool_context: ToolContext,
    aircraft_callsign: str,
    departure_runway: str,
    taxi_route: str | None = None,
) -> dict[str, Any]:
    """Provide taxi clearance procedure and phraseology.
    
    Use this tool when a pilot advises ready to taxi for departure.
    Provides the correct taxi clearance format and hold short instructions.
    
    Args:
        tool_context: ADK tool context
        aircraft_callsign: Aircraft callsign
        departure_runway: Runway for departure (e.g., "27", "09", "34L")
        taxi_route: Optional specific taxi route (e.g., "via Alpha, Bravo")
    
    Returns:
        Dictionary with taxi clearance information and phraseology guidance
    """
    
    # Build taxi clearance
    clearance_parts = [
        f"{aircraft_callsign}",
    ]
    
    if taxi_route:
        clearance_parts.append(f"taxi to runway {departure_runway} via {taxi_route}")
    else:
        clearance_parts.append(f"taxi to runway {departure_runway}")
    
    clearance_parts.append(f"hold short of runway {departure_runway}")
    
    standard_clearance = ", ".join(clearance_parts)
    
    return {
        "procedure_type": "taxi_clearance",
        "aircraft_callsign": aircraft_callsign,
        "departure_runway": departure_runway,
        "taxi_route": taxi_route or "Direct (no specific route required)",
        "standard_phraseology": standard_clearance,
        "pilot_required_readback": f"Taxi runway {departure_runway}{' via ' + taxi_route if taxi_route else ''}, hold short runway {departure_runway}, {aircraft_callsign}",
        "required_elements": {
            "destination": f"Runway {departure_runway}",
            "route": taxi_route or "Not specified - pilot's discretion",
            "hold_short": f"Runway {departure_runway} (mandatory readback)",
            "active_runway_crossings": "Any active runways must be explicitly cleared to cross"
        },
        "safety_critical_items": [
            "ALWAYS include hold short instruction",
            "NEVER clear aircraft to cross active runway without explicit instruction",
            "Verify pilot reads back runway assignment and hold short"
        ]
    }