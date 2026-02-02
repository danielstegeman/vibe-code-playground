"""Agent definitions for Monty Python improv system"""

# Lazy loading to avoid circular imports
_director_agent = None
_john_agent = None
_graham_agent = None
_terry_j_agent = None
_terry_g_agent = None
_eric_agent = None
_michael_agent = None


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


__all__ = [
    'get_director_agent',
    'get_john_agent',
    'get_graham_agent',
    'get_terry_j_agent',
    'get_terry_g_agent',
    'get_eric_agent',
    'get_michael_agent',
]
