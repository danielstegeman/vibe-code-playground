"""Orchestrator Agent -- routes user requests to specialist agents."""

from google.adk.agents.llm_agent import Agent

from ..config import Config
from .devices_agent import devices_agent
from .schedule_agent import schedule_agent
from .info_agent import info_agent

orchestrator_agent = Agent(
    model=Config.MODEL_NAME,
    name="orchestrator_agent",
    description=(
        "Top-level orchestrator that receives user requests and delegates "
        "to the appropriate specialist agent(s): devices_agent, "
        "schedule_agent, or info_agent."
    ),
    instruction=(
        "You are the Home Assistant orchestrator. "
        "Your job is to understand what the user wants and delegate to the "
        "right specialist agent. You do NOT call tools directly -- you "
        "transfer the task to a sub-agent.\n\n"
        "Routing rules:\n"
        "- Requests about lights, dimming, brightness, locks, unlocking, "
        "  thermostats or blinds -> transfer to devices_agent\n"
        "- Requests about calendar, schedule, reminders, tonight, tomorrow "
        "  or appointments -> transfer to schedule_agent\n"
        "- Requests about weather, temperature outside, sunset, shopping "
        "  list or buying items -> transfer to info_agent\n"
        "- Compound requests (e.g. 'set the mood for movie night') may "
        "  require multiple agents. Handle each part and compose a single "
        "  coherent reply.\n\n"
        "Always respond in a friendly, concise manner. Combine sub-agent "
        "results into one natural answer for the user."
    ),
    sub_agents=[devices_agent, schedule_agent, info_agent],
)
