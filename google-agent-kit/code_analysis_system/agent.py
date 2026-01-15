"""ADK-compliant agent definition for the code analysis system.

This module exposes the root_agent for use with the ADK CLI and web interface.
"""

# Import agents directly (not through __init__.py to avoid circular imports)
from code_analysis_system.agents.director import director_agent
from code_analysis_system.agents.librarian import librarian_agent
from code_analysis_system.agents.mediator import mediator_agent
from code_analysis_system.agents.subdomain import create_subdomain_agent

# Export the director agent as the root agent
# The director is the entry point for the multi-agent system
root_agent = director_agent

# Also export other agents for direct access if needed
__all__ = [
    'root_agent',
    'director_agent',
    'librarian_agent',
    'mediator_agent',
    'create_subdomain_agent',
]
