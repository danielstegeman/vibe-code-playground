"""Director agent for synthesizing review findings."""

from swarms import Agent
from pathlib import Path
from core.utils import load_prompt_from_file


def load_prompt() -> str:
    """Load the director prompt from markdown file."""
    prompt_path = Path(__file__).parent / "prompt.md"
    return load_prompt_from_file(prompt_path)


def create_director(model_name: str = "gpt-4o") -> Agent:
    """Create director agent that synthesizes all review findings."""
    return Agent(
        agent_name="Review-Director",
        system_prompt=load_prompt(),
        model_name=model_name,
        max_loops=1,
        context_length=30000,
    
        streaming_on=False,
        verbose=False,
        temperature=0.7,
        top_p=None,
        retry_attempts=3,
        retry_interval=200,
    )
