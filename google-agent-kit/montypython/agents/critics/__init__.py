"""Critic agents for consistency evaluation"""

from .critic_john import critic_john_agent
from .critic_eric import critic_eric_agent
from .critic_michael import critic_michael_agent
from .critic_graham import critic_graham_agent
from .critic_terry_j import critic_terry_j_agent
from .critic_terry_g import critic_terry_g_agent
from .critic_director import critic_director_agent
from .critic_aggregator import critic_aggregator_agent

__all__ = [
    'critic_john_agent',
    'critic_eric_agent',
    'critic_michael_agent',
    'critic_graham_agent',
    'critic_terry_j_agent',
    'critic_terry_g_agent',
    'critic_director_agent',
    'critic_aggregator_agent',
]
