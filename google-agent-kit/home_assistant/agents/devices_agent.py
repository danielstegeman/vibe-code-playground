"""Devices Agent -- controls smart-home devices."""

from google.adk.agents.llm_agent import Agent

from ..config import Config
from ..tools.device_tools import get_device_state, set_device_state

devices_agent = Agent(
    model=Config.MODEL_NAME,
    name="devices_agent",
    description=(
        "Specialist agent that controls smart-home devices such as lights, "
        "locks, thermostats and blinds. Delegates to get_device_state and "
        "set_device_state tools."
    ),
    instruction=(
        "You are a smart-home device controller. "
        "When the user asks you to check or change a device, use the "
        "get_device_state tool to read the current state and "
        "set_device_state to apply changes. "
        "Always confirm the action you took in a short, friendly sentence. "
        "If brightness is mentioned as a percentage, pass it as an integer "
        "(e.g. 30 for 30%). "
        "Common device IDs: lights_living_room, lights_kitchen, "
        "lock_front_door, thermostat_main."
    ),
    tools=[get_device_state, set_device_state],
)
