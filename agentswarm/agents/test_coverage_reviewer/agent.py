"""Test coverage and quality reviewer agent."""

from swarms import Agent
from pathlib import Path
from core.utils import load_prompt_from_file


def load_prompt() -> str:
    """Load the test coverage reviewer prompt from markdown file."""
    prompt_path = Path(__file__).parent / "prompt.md"
    return load_prompt_from_file(prompt_path)


def create_test_coverage_reviewer(model_name: str = "gpt-4o") -> Agent:
    """Create test coverage and quality reviewer agent."""
    return Agent(
        agent_name="Test-Coverage-Reviewer",
        system_prompt=load_prompt(),
        model_name=model_name,
        max_loops=2,
        context_length=200000,
        streaming_on=False,
        verbose=False,
        temperature=0.7,
        top_p=None,
    )
