"""Root agent definition for Monty Python Improv System"""

from .agents.director import root_agent as multi_agent_root
from .agents.director import get_single_agent_director
from .config import Config

# ADK expects root_agent at this location
# Select between multi-agent and single-agent mode based on config
if Config.USE_SINGLE_AGENT:
    root_agent = get_single_agent_director()
else:
    root_agent = multi_agent_root

