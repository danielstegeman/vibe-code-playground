"""Schedule Agent -- manages calendar events."""

from google.adk.agents.llm_agent import Agent

from ..config import Config
from ..tools.calendar_tools import get_calendar_events, create_calendar_event

schedule_agent = Agent(
    model=Config.MODEL_NAME,
    name="schedule_agent",
    description=(
        "Specialist agent that queries and creates calendar events. "
        "Handles scheduling, reminders, and checking availability."
    ),
    instruction=(
        "You are a personal schedule assistant. "
        "When the user asks about upcoming events, use get_calendar_events "
        "with the appropriate date. When asked to create an event, use "
        "create_calendar_event. "
        "If no events are found, respond with a friendly 'nothing scheduled'. "
        "Always include the date and time in your response."
    ),
    tools=[get_calendar_events, create_calendar_event],
)
