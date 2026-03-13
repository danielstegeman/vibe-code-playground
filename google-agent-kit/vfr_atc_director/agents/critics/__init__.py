"""ATC Phraseology and Procedure Critics.

This package contains critic sub-agents that review and correct
ATC communications for compliance with ICAO/EASA standards.
"""

# Lazy loading to avoid circular imports
_phraseology_critic_agent = None


def get_phraseology_critic_agent():
    """Get the phraseology critic agent instance (lazy loaded).
    
    Returns:
        Agent: The phraseology critic agent.
    """
    global _phraseology_critic_agent
    if _phraseology_critic_agent is None:
        from .phraseology_critic import phraseology_critic_agent
        _phraseology_critic_agent = phraseology_critic_agent
    return _phraseology_critic_agent


__all__ = ['get_phraseology_critic_agent']
