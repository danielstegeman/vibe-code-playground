"""Scene management tools for the improv system"""

import random
from typing import List, Dict, Any


def get_scene_flow_distribution() -> Dict[str, Any]:
    """
    Calculate scene flow distribution based on MIN_TURNS and MAX_TURNS settings.
    
    Returns:
        Dictionary with scene phase boundaries and thresholds:
        {
            "early_end": int,        # Last turn of early phase
            "mid_end": int,          # Last turn of mid phase (== min_turns)
            "peak_end": int,         # Last turn of peak phase (== max_turns)
            "min_turns": int,        # Minimum required turns
            "max_turns": int         # Maximum allowed turns
        }
    """
    from ..config import Config
    
    min_turns = Config.MIN_TURNS
    max_turns = Config.MAX_TURNS
    
    # Calculate early phase end
    # For very small min_turns (1-2), early phase is just turn 1
    # For larger min_turns, take ~40% of minimum
    if min_turns <= 2:
        early_end = 1
    else:
        early_end = max(1, int(min_turns * 0.4))
        # Ensure early_end is at least 1 less than min_turns to have a mid phase
        early_end = min(early_end, min_turns - 1)
    
    # Mid phase ends at min_turns
    mid_end = min_turns
    
    # Peak phase ends at max_turns
    peak_end = max_turns
    
    return {
        "early_end": early_end,
        "mid_end": mid_end,
        "peak_end": peak_end,
        "min_turns": min_turns,
        "max_turns": max_turns
    }


def initiate_dialogue_exchange(agent_a: str, agent_b: str, exchange_turns: int = 4) -> Dict[str, Any]:
    """
    Initiate a rapid dialogue exchange between two performers.
    
    This signals that the director should alternate between these two agents
    for the specified number of turns to create back-and-forth dialogue.
    
    Args:
        agent_a: First performer agent name (e.g., 'john_agent')
        agent_b: Second performer agent name (e.g., 'michael_agent')
        exchange_turns: Number of turns to maintain the exchange (default: 4)
        
    Returns:
        Dictionary with exchange pattern:
        {
            "mode": "dialogue_exchange",
            "participants": [agent_a, agent_b],
            "turns_remaining": int,
            "pattern": [agent_a, agent_b, agent_a, agent_b, ...]
        }
    """
    # Create alternating pattern
    pattern = [agent_a if i % 2 == 0 else agent_b for i in range(exchange_turns)]
    
    return {
        "mode": "dialogue_exchange",
        "participants": [agent_a, agent_b],
        "turns_remaining": exchange_turns,
        "pattern": pattern,
        "instruction": f"Alternate between {agent_a} and {agent_b} for {exchange_turns} turns. Each should respond in DIALOGUE mode: 1-2 sentences, direct address, ending with question or challenge to sustain momentum."
    }


def increment_turn_count() -> int:
    """
    Increment and return the current turn count.
    
    Returns:
        Updated turn count
    """
    # The director will handle turn counting via instructions
    # This is a placeholder tool that the LLM can call
    return 1


def get_sentence_count() -> int:
    """
    Get a random number of sentences the performer should say.
    
    Returns:
        Random number between 1 and 3 (inclusive)
    """
    return random.randint(1, 3)


def get_action_count() -> int:
    """
    Get a random number of actions/stage directions the performer should include.
    
    Returns:
        Random number between 0 and 2 (inclusive)
    """
    return random.randint(0, 2)
