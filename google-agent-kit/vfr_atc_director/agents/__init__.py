"""Specialist ATC controller sub-agents.

This package contains specialist controllers and critic agents:
- Tower controller (pattern work, takeoff/landing clearances)
- Ground controller (taxiway routing, ramp operations)
- Clearance delivery (IFR/VFR clearances)
- Approach/Departure controller (airborne traffic outside pattern)
- Phraseology critic (reviews communications for ICAO/EASA compliance)

Sub-agents will be implemented in subsequent steps.
"""

from .critics import get_phraseology_critic_agent

__all__ = ['get_phraseology_critic_agent']
