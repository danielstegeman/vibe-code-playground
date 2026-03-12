"""Root agent entry point for ADK discovery.

ADK expects a module-level ``root_agent`` in this file.
"""

from .agents.orchestrator_agent import orchestrator_agent

root_agent = orchestrator_agent
