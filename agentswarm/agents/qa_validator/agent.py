"""QA Validator agent for plan-output validation."""

from swarms import Agent
from pathlib import Path
from core.utils import load_prompt_from_file


def load_prompt() -> str:
    """Load the QA validator prompt from markdown file."""
    prompt_path = Path(__file__).parent / "prompt.md"
    return load_prompt_from_file(prompt_path)


def create_qa_validator(model_name: str = "gpt-4o") -> Agent:
    """Create QA validator agent that checks plan-output alignment."""
    return Agent(
        agent_name="QA-Validator",
        system_prompt=load_prompt(),
        model_name=model_name,
        max_loops=1,
        context_length=200000,
        streaming_on=False,
        verbose=False,
        temperature=0.7,
        top_p=None,
    )
