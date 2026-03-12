"""Tests for specialist and orchestrator agents.

These tests verify agent wiring -- correct tools, sub-agents, and
configuration -- without making live LLM calls.
"""

import pytest

from home_assistant.agents.devices_agent import devices_agent
from home_assistant.agents.schedule_agent import schedule_agent
from home_assistant.agents.info_agent import info_agent
from home_assistant.agents.orchestrator_agent import orchestrator_agent
from home_assistant.agent import root_agent
from home_assistant.tools.device_tools import get_device_state, set_device_state
from home_assistant.tools.calendar_tools import get_calendar_events, create_calendar_event
from home_assistant.tools.info_tools import get_weather, get_shopping_list, add_to_shopping_list


# -- Devices Agent --

class TestDevicesAgent:
    def test_has_correct_name(self):
        assert devices_agent.name == "devices_agent"

    def test_has_device_tools(self):
        tool_names = {t.__name__ for t in devices_agent.tools}
        assert "get_device_state" in tool_names
        assert "set_device_state" in tool_names

    def test_has_no_sub_agents(self):
        assert devices_agent.sub_agents == []

    def test_description_mentions_devices(self):
        assert "device" in devices_agent.description.lower()


# -- Schedule Agent --

class TestScheduleAgent:
    def test_has_correct_name(self):
        assert schedule_agent.name == "schedule_agent"

    def test_has_calendar_tools(self):
        tool_names = {t.__name__ for t in schedule_agent.tools}
        assert "get_calendar_events" in tool_names
        assert "create_calendar_event" in tool_names

    def test_has_no_sub_agents(self):
        assert schedule_agent.sub_agents == []


# -- Info Agent --

class TestInfoAgent:
    def test_has_correct_name(self):
        assert info_agent.name == "info_agent"

    def test_has_info_tools(self):
        tool_names = {t.__name__ for t in info_agent.tools}
        assert "get_weather" in tool_names
        assert "get_shopping_list" in tool_names
        assert "add_to_shopping_list" in tool_names

    def test_has_no_sub_agents(self):
        assert info_agent.sub_agents == []


# -- Orchestrator Agent --

class TestOrchestratorAgent:
    def test_has_correct_name(self):
        assert orchestrator_agent.name == "orchestrator_agent"

    def test_has_all_sub_agents(self):
        sub_names = {a.name for a in orchestrator_agent.sub_agents}
        assert sub_names == {"devices_agent", "schedule_agent", "info_agent"}

    def test_does_not_have_tools(self):
        assert orchestrator_agent.tools == []

    def test_description_mentions_orchestrator(self):
        assert "orchestrator" in orchestrator_agent.description.lower()

    def test_instruction_contains_routing_rules(self):
        instr = orchestrator_agent.instruction.lower()
        for keyword in ["lights", "calendar", "weather", "shopping"]:
            assert keyword in instr, f"Missing routing keyword: {keyword}"


# -- Root agent --

class TestRootAgent:
    def test_root_is_orchestrator(self):
        assert root_agent is orchestrator_agent

    def test_root_agent_name(self):
        assert root_agent.name == "orchestrator_agent"
