# PR Review Swarm - Code Structure

This document describes the new vertical slice architecture implemented for the PR Review Swarm.

## Directory Structure

```
agentswarm/
├── agents/                          # Agent vertical slices
│   ├── security_reviewer/
│   │   ├── __init__.py
│   │   ├── agent.py                 # Agent creation logic
│   │   └── prompt.md                # System prompt (externalized)
│   │
│   ├── code_quality_reviewer/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── prompt.md
│   │
│   ├── test_coverage_reviewer/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── prompt.md
│   │
│   ├── documentation_reviewer/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── prompt.md
│   │
│   ├── qa_validator/
│   │   ├── __init__.py
│   │   ├── agent.py                 # QA validator agent
│   │   ├── parser.py                # Output parsing logic
│   │   └── prompt.md
│   │
│   ├── director/
│   │   ├── __init__.py
│   │   ├── agent.py                 # Director synthesis agent
│   │   └── prompt.md
│   │
│   └── __init__.py                  # Exports all agents + create_all_reviewers()
│
├── core/                            # Core domain models
│   ├── __init__.py
│   ├── models.py                    # ReviewArtifact, Discrepancy, Severity
│   └── utils.py                     # Utility functions (load_prompt_from_file)
│
├── infrastructure/                  # External integrations
│   ├── github/
│   │   ├── __init__.py
│   │   └── client.py                # GitHubClient, fetch_github_pr()
│   │
│   ├── logging/
│   │   ├── __init__.py
│   │   └── logger.py                # ReviewLogger with colored output
│   │
│   └── __init__.py
│
├── services/                        # Application services
│   ├── __init__.py
│   ├── orchestrator.py              # run_pr_review() - main workflow
│   └── report_generator.py          # Markdown report generation
│
├── config/                          # Configuration management
│   ├── __init__.py
│   └── settings.py                  # MODEL_NAME, GitHub config, API validation
│
├── scripts/                         # Utility scripts
│   └── test_claude.py               # API connectivity test
│
├── outputs/                         # Generated outputs
│   └── reports/                     # Generated markdown reports
│
├── main.py                          # Minimal entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Architecture Principles

### 1. Vertical Slice Architecture
Each agent is self-contained in its own folder with:
- `agent.py` - Agent creation logic
- `prompt.md` - Externalized system prompt
- `parser.py` - Optional output parsing (for QA validator)

**Benefits:**
- Easy to find and modify agent-specific code
- Prompts are version-controlled as markdown
- Clear ownership and responsibility
- Simple to add new agents (copy folder template)

### 2. Layered Architecture
- **Agents Layer**: Domain-specific reviewers and validators
- **Core Layer**: Shared domain models and utilities
- **Infrastructure Layer**: External integrations (GitHub, logging)
- **Services Layer**: Application orchestration and business logic
- **Config Layer**: Centralized configuration management

### 3. Externalized Prompts
All system prompts are stored as `.md` files, loaded at runtime:
```python
def load_prompt() -> str:
    prompt_path = Path(__file__).parent / "prompt.md"
    return prompt_path.read_text(encoding='utf-8')
```

**Benefits:**
- Edit prompts without touching Python code
- Better version control diffs
- Easy to review prompt changes
- Non-developers can modify prompts

### 4. Centralized Configuration
All configuration in `config/settings.py`:
- Model selection
- GitHub repository settings
- Output directories
- API key validation

Environment variables loaded from `.env` file.

## Import Patterns

### From main.py
```python
from config import MODEL_NAME, validate_api_key
from infrastructure.github import fetch_github_pr, GitHubClient
from services import run_pr_review
```

### From services/orchestrator.py
```python
from agents import create_all_reviewers, create_qa_validator, create_director, parse_qa_validation
from core.models import ReviewArtifact
from infrastructure.logging import ReviewLogger
from .report_generator import generate_markdown_report
```

### From agents
```python
from agents.security_reviewer import create_security_reviewer
from agents.qa_validator import parse_qa_validation
from agents import create_all_reviewers  # Convenience function
```

## Running the Application

```bash
# Activate virtual environment
.\Scripts\activate  # Windows
source bin/activate  # Linux/Mac

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and GitHub settings

# Run main application
python main.py

# Test Claude connectivity
python scripts/test_claude.py
```

## Adding a New Agent

1. Create a new folder in `agents/`:
```bash
mkdir agents/new_reviewer
```

2. Create `__init__.py`:
```python
from .agent import create_new_reviewer
__all__ = ['create_new_reviewer']
```

3. Create `agent.py`:
```python
from swarms import Agent
from pathlib import Path

def load_prompt() -> str:
    prompt_path = Path(__file__).parent / "prompt.md"
    return prompt_path.read_text(encoding='utf-8')

def create_new_reviewer(model_name: str = "gpt-4o") -> Agent:
    return Agent(
        agent_name="New-Reviewer",
        system_prompt=load_prompt(),
        model_name=model_name,
        max_loops=2,
        context_length=200000,
        streaming_on=False,
        verbose=False,
        temperature=0.7,
        top_p=None,
    )
```

4. Create `prompt.md` with your system prompt

5. Update `agents/__init__.py` to export the new agent

6. Add to `create_all_reviewers()` in `agents/__init__.py`

## Migration from Old Structure

Old files (kept for backward compatibility, will be removed):
- `reviewers.py` → `agents/*/agent.py`
- `qa_validator.py` → `agents/qa_validator/`
- `director.py` → `agents/director/`
- `review_artifact.py` → `core/models.py`
- `logger.py` → `infrastructure/logging/logger.py`
- `github_client.py` → `infrastructure/github/client.py`
- `report_generator.py` → `services/report_generator.py`
- `test_claude.py` → `scripts/test_claude.py`

All orchestration logic from `main.py` moved to `services/orchestrator.py`.

## Key Improvements

1. **Maintainability**: Each component has a clear location
2. **Testability**: Modular structure enables easier unit testing
3. **Scalability**: Easy to add new agents or reviewers
4. **Clarity**: Prompts are separate from code
5. **Configuration**: Centralized settings management
6. **Documentation**: Self-documenting folder structure
