"""Security-focused code reviewer agent."""

from swarms import Agent
from pathlib import Path
from core.utils import load_prompt_from_file


def load_prompt() -> str:
    """Load the security reviewer prompt from markdown file."""
    prompt_path = Path(__file__).parent / "prompt.md"
    return load_prompt_from_file(prompt_path)


def create_security_reviewer(model_name: str = "gpt-4o") -> Agent:
    """Create security-focused code reviewer agent."""
    return Agent(
        agent_name="Security-Reviewer",
        system_prompt=load_prompt(),
        model_name=model_name,
        max_loops=2,
        dynamic_context_window=True,
        streaming_on=False,
        verbose=False,
        temperature=0.7,
        top_p=None,
        retry_attempts=3,
        retry_interval=200,
    )
