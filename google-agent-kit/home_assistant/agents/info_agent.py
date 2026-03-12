"""Info Agent -- weather, shopping list and general information."""

from google.adk.agents.llm_agent import Agent

from ..config import Config
from ..tools.info_tools import get_weather, get_shopping_list, add_to_shopping_list

info_agent = Agent(
    model=Config.MODEL_NAME,
    name="info_agent",
    description=(
        "Specialist agent that provides weather information and manages the "
        "shopping list. Handles queries about temperature, sunset, and "
        "grocery items."
    ),
    instruction=(
        "You are an information assistant. "
        "For weather queries, use get_weather with the user's location "
        "(default 'Home'). Include condition, temperature and sunset time "
        "in your answer. "
        "For shopping-list queries, use get_shopping_list to read the list "
        "and add_to_shopping_list to add items. "
        "Keep answers concise and friendly."
    ),
    tools=[get_weather, get_shopping_list, add_to_shopping_list],
)
