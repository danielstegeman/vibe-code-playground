"""Core utilities."""

from pathlib import Path
from config import MINIMAL_TOKEN_MODE


# Minimal placeholder prompt for testing (conserves tokens)
MINIMAL_PROMPT = "You are a code reviewer. Provide a brief review response."


def load_prompt_from_file(prompt_path: Path) -> str:
    """
    Load a prompt from a markdown file.
    Automatically uses minimal prompt if MINIMAL_TOKEN_MODE is enabled.
    
    Args:
        prompt_path: Path to the prompt markdown file
        
    Returns:
        The prompt text as a string (or minimal prompt if in minimal token mode)
    """
    if MINIMAL_TOKEN_MODE:
        return MINIMAL_PROMPT
    return prompt_path.read_text(encoding='utf-8')
