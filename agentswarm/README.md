# PR Review Swarm

A multi-agent system for automated pull request reviews using the Swarms framework.

## Features

- **Multi-Agent Review**: 4 specialized agents (Security, Code Quality, Testing, Documentation)
- **Two-Phase Execution**: Each agent creates a plan, then executes review
- **QA Validation**: Dedicated agent validates plan-output alignment
- **Observability**: Colored console logging with discrepancy highlighting
- **Human-in-the-Loop**: Flags critical discrepancies for engineer review
- **Markdown Reports**: Comprehensive review reports saved locally

## Architecture

```
Reviewers (parallel) → QA Validator → Director → Markdown Report
    ↓
  Plan Phase (Loop 1)
  Execution Phase (Loop 2)
```

## Setup

1. **Create virtual environment** (if not already done):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```powershell
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env and add your API key
   # OPENAI_API_KEY=your-key-here
   ```

## Usage

Run the PR review:

```powershell
python main.py
```

The script will:
1. Initialize 4 reviewer agents + QA validator + Director
2. Each reviewer creates a plan, then executes review
3. QA validator checks plan-output alignment
4. Director synthesizes all findings
5. Generate markdown report in `reviews/` directory

## Agents

### Specialized Reviewers

1. **Security-Reviewer**
   - SQL injection, XSS, CSRF vulnerabilities
   - Authentication/authorization issues
   - Secrets in code
   - Dependency security

2. **Code-Quality-Reviewer**
   - SOLID principles
   - Design patterns
   - Code complexity
   - Error handling

3. **Test-Coverage-Reviewer**
   - Unit test coverage
   - Edge cases
   - Test quality
   - Mock usage

4. **Documentation-Reviewer**
   - Code comments
   - Docstrings
   - README updates
   - API documentation

### QA Validator

- Compares agent plans vs outputs
- Detects scope drift, missed items, hallucinations
- Flags discrepancies with severity (critical/major/minor)
- Logs to console with "NEEDS HUMAN REVIEW" markers

### Director

- Synthesizes all findings
- Provides final recommendation (Approve/Request Changes/Reject)
- Prioritizes issues by severity
- Flags QA concerns for human review

## Output

### Console

- Colored progress logging
- Discrepancy highlighting (red for critical, yellow for major)
- Human review flags
- Completion summary

### Markdown Report

Saved to `reviews/pr_review_<number>_<timestamp>.md`:

- Executive summary
- QA validation findings
- Detailed agent reviews (plan + execution)
- Human review required section
- Table of contents

## Customization

Edit agent prompts in:
- `reviewers.py` - Specialized reviewer agents
- `qa_validator.py` - QA validation logic
- `director.py` - Director synthesis

Adjust logging verbosity in `main.py`:
```python
logger = ReviewLogger(verbose=True)  # Set to False for minimal output
```

## Future Enhancements

- [ ] GitHub API integration (fetch PR diffs automatically)
- [ ] GitHub PR comment integration (post reviews directly)
- [ ] Additional specialized agents (Performance, Accessibility)
- [ ] Configurable agent selection per PR type
- [ ] Webhook support for CI/CD integration

## Requirements

- Python 3.10+
- OpenAI API key (or other LLM provider)
- See `requirements.txt` for full dependencies

## License

MIT
