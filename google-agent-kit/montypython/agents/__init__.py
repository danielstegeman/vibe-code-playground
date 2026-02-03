"""Agent definitions for Monty Python improv system"""

# Lazy loading to avoid circular imports
_director_agent = None
_john_agent = None
_graham_agent = None
_terry_j_agent = None
_terry_g_agent = None
_eric_agent = None
_michael_agent = None
_critic_john_agent = None
_critic_eric_agent = None
_critic_michael_agent = None
_critic_graham_agent = None
_critic_terry_j_agent = None
_critic_terry_g_agent = None
_critic_director_agent = None
_critic_aggregator_agent = None


def get_director_agent():
    """Lazy load director agent"""
    global _director_agent
    if _director_agent is None:
        from .director import director_agent
        _director_agent = director_agent
    return _director_agent


def get_john_agent():
    """Lazy load John Cleese agent"""
    global _john_agent
    if _john_agent is None:
        from .john import john_agent
        _john_agent = john_agent
    return _john_agent


def get_graham_agent():
    """Lazy load Graham Chapman agent"""
    global _graham_agent
    if _graham_agent is None:
        from .graham import graham_agent
        _graham_agent = graham_agent
    return _graham_agent


def get_terry_j_agent():
    """Lazy load Terry Jones agent"""
    global _terry_j_agent
    if _terry_j_agent is None:
        from .terry_j import terry_j_agent
        _terry_j_agent = terry_j_agent
    return _terry_j_agent


def get_terry_g_agent():
    """Lazy load Terry Gilliam agent"""
    global _terry_g_agent
    if _terry_g_agent is None:
        from .terry_g import terry_g_agent
        _terry_g_agent = terry_g_agent
    return _terry_g_agent


def get_eric_agent():
    """Lazy load Eric Idle agent"""
    global _eric_agent
    if _eric_agent is None:
        from .eric import eric_agent
        _eric_agent = eric_agent
    return _eric_agent


def get_michael_agent():
    """Lazy load Michael Palin agent"""
    global _michael_agent
    if _michael_agent is None:
        from .michael import michael_agent
        _michael_agent = michael_agent
    return _michael_agent


def get_single_agent_director():
    """Lazy load single-agent director"""
    from .director import get_single_agent_director as _get_single
    return _get_single()


def get_critic_john_agent():
    """Lazy load John Cleese critic agent"""
    global _critic_john_agent
    if _critic_john_agent is None:
        from .critics.critic_john import critic_john_agent
        _critic_john_agent = critic_john_agent
    return _critic_john_agent


def get_critic_eric_agent():
    """Lazy load Eric Idle critic agent"""
    global _critic_eric_agent
    if _critic_eric_agent is None:
        from .critics.critic_eric import critic_eric_agent
        _critic_eric_agent = critic_eric_agent
    return _critic_eric_agent


def get_critic_michael_agent():
    """Lazy load Michael Palin critic agent"""
    global _critic_michael_agent
    if _critic_michael_agent is None:
        from .critics.critic_michael import critic_michael_agent
        _critic_michael_agent = critic_michael_agent
    return _critic_michael_agent


def get_critic_graham_agent():
    """Lazy load Graham Chapman critic agent"""
    global _critic_graham_agent
    if _critic_graham_agent is None:
        from .critics.critic_graham import critic_graham_agent
        _critic_graham_agent = critic_graham_agent
    return _critic_graham_agent


def get_critic_terry_j_agent():
    """Lazy load Terry Jones critic agent"""
    global _critic_terry_j_agent
    if _critic_terry_j_agent is None:
        from .critics.critic_terry_j import critic_terry_j_agent
        _critic_terry_j_agent = critic_terry_j_agent
    return _critic_terry_j_agent


def get_critic_terry_g_agent():
    """Lazy load Terry Gilliam critic agent"""
    global _critic_terry_g_agent
    if _critic_terry_g_agent is None:
        from .critics.critic_terry_g import critic_terry_g_agent
        _critic_terry_g_agent = critic_terry_g_agent
    return _critic_terry_g_agent


def get_critic_director_agent():
    """Lazy load director critic agent"""
    global _critic_director_agent
    if _critic_director_agent is None:
        from .critics.critic_director import critic_director_agent
        _critic_director_agent = critic_director_agent
    return _critic_director_agent


def get_critic_aggregator_agent():
    """Lazy load critic aggregator agent"""
    global _critic_aggregator_agent
    if _critic_aggregator_agent is None:
        from .critics.critic_aggregator import critic_aggregator_agent
        _critic_aggregator_agent = critic_aggregator_agent
    return _critic_aggregator_agent


__all__ = [
    'get_director_agent',
    'get_john_agent',
    'get_graham_agent',
    'get_terry_j_agent',
    'get_terry_g_agent',
    'get_eric_agent',
    'get_michael_agent',
    'get_single_agent_director',
    'get_critic_john_agent',
    'get_critic_eric_agent',
    'get_critic_michael_agent',
    'get_critic_graham_agent',
    'get_critic_terry_j_agent',
    'get_critic_terry_g_agent',
    'get_critic_director_agent',
    'get_critic_aggregator_agent',
]
