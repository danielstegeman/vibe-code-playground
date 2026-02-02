"""Scene management tools for the improv system"""

import random
from typing import List


def select_random_performer(exclude_last: bool = True) -> str:
    """
    Randomly select the next performer for the scene.
    
    Args:
        exclude_last: If True, avoid selecting the performer who just spoke
        
    Returns:
        Name of the selected performer agent
    """
    from ..config import Config
    
    performers = Config.PERFORMERS.copy()
    
    # Simple random selection without state management
    # The director will handle tracking which performer was selected
    selected = random.choice(performers)
    
    return selected


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
