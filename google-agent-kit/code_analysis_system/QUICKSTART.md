# Quick Start Guide

## Multi-Agent Linux Kernel Analysis System

This system analyzes the Linux kernel codebase using 4 specialized AI agents that work together to answer your questions.

## Setup (One-Time)

1. **Ensure indexes exist:**
   ```bash
   cd google-agent-kit
   python repo_indexer_agent/tests/generate_linux_indexes.py
   ```

2. **Verify API key:**
   Make sure `ANTHROPIC_API_KEY` is set in your `.env` file

3. **Test the system:**
   ```bash
   python code_analysis_system/test_system.py
   ```

## Usage

### Interactive Mode

```bash
cd google-agent-kit
python code_analysis_system/main.py
```

Then enter queries like:
- How does the Linux scheduler work?
- What is the memory management subsystem?
- Explain the VFS layer
- How does ext4 handle journaling?

### Programmatic Usage

```python
from code_analysis_system.orchestrator import run_analysis

# Ask a question
answer = run_analysis("How does the Linux scheduler work?")
print(answer)

# With custom LOC limit per agent
answer = run_analysis(
    "Explain memory management",
    max_lines_per_agent=50000  # Smaller agents
)
```

### Custom Orchestration

```python
from code_analysis_system.orchestrator import CodeAnalysisOrchestrator

# Create orchestrator with custom settings
orchestrator = CodeAnalysisOrchestrator(max_lines_per_agent=75000)

# Run analysis
answer = orchestrator.analyze("How does the network stack work?")
```

## How It Works

### The 5-Phase Process

1. **Planning** (Director)
   - Receives your query
   - Creates an analysis plan
   - Determines what information is needed

2. **Location Discovery** (Librarian)
   - Consults pre-generated indexes
   - Identifies relevant code subdomains
   - Provides LOC estimates and paths

3. **Agent Allocation** (Director)
   - Decides how many subdomain agents needed
   - Splits work based on LOC limits
   - Assigns specific paths to each agent

4. **Code Analysis** (Subdomain Agents)
   - Each agent analyzes its assigned code
   - Reads source files strategically
   - Extracts relevant information
   - Provides file references

5. **Synthesis** (Mediator)
   - Aggregates all findings
   - Resolves conflicts
   - Identifies gaps
   - Formats final comprehensive answer

## Example Session

```
> How does the Linux scheduler work?

[Phase 1] Director: Formulating analysis plan...
Director's plan: Analyze process scheduling subsystem, focusing on 
scheduler core, CFS implementation, and task structures...

[Phase 2] Librarian: Identifying relevant code locations...
Librarian's recommendations: 
- [kernel] subdomain: kernel/sched/ (~65,958 LOC)
- Key files: core.c, fair.c, sched.h

[Phase 3] Director: Allocating subdomain agents...
Agent allocation: Single agent sufficient (65K < 100K limit)

[Phase 4] Subdomain Agent: Analyzing code...
Analyzing kernel/sched/core.c, fair.c, and related files...

[Phase 5] Mediator: Synthesizing final answer...

FINAL ANSWER:
The Linux scheduler uses the Completely Fair Scheduler (CFS)...
[detailed answer with file references]
```

## Configuration

Edit [code_analysis_system/config.py](code_analysis_system/config.py):

```python
# Lines of code per subdomain agent
MAX_LINES_PER_SUBDOMAIN_AGENT = 100000

# Max lines to read from a single file
MAX_FILE_READ_LINES = 1000

# LLM settings
MODEL_NAME = "anthropic/claude-sonnet-4-5-20250929"
MODEL_TIMEOUT = 300
```

## Troubleshooting

### "Index file not found"
Run the indexer first: `python repo_indexer_agent/tests/generate_linux_indexes.py`

### "Linux repository not found"
Ensure `linux_repo/` exists in `google-agent-kit/`

### "API key not found"
Set `ANTHROPIC_API_KEY` in your `.env` file

### Slow responses
- Increase `MODEL_TIMEOUT` in config.py
- Reduce `MAX_LINES_PER_SUBDOMAIN_AGENT` to create more, smaller agents
- Try simpler, more focused queries

## Tips for Good Questions

✅ **Good Questions:**
- "How does the Linux scheduler prioritize processes?"
- "What data structures are used in memory management?"
- "Explain the ext4 journaling mechanism"
- "How does the network stack handle packet routing?"

❌ **Too Broad:**
- "Explain everything about Linux"
- "How does the kernel work?"

❌ **Too Specific Without Context:**
- "What is line 142 of sched.c?"
- "Why is this function called here?"

## Architecture Overview

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ Query
       ▼
┌─────────────────┐
│    Director     │ ◄──┐
│   (Planning &   │    │
│  Coordination)  │    │
└────────┬────────┘    │
         │             │
         ▼             │
┌─────────────────┐    │
│   Librarian     │    │
│  (Index Lookup) │    │
└────────┬────────┘    │
         │             │
         ▼             │
┌─────────────────┐    │
│   Subdomain     │    │
│  Agent(s) 1..N  │ ───┘ (can request more agents)
│ (Code Analysis) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Mediator     │
│  (Synthesis)    │
└────────┬────────┘
         │ Answer
         ▼
    ┌─────────┐
    │  User   │
    └─────────┘
```

## Available Subdomains

The system knows about these Linux kernel subdomains:

**Core:**
- kernel - Process management & scheduling
- mm - Memory management
- locking - Synchronization

**Filesystems:**
- fs - VFS layer
- ext4, btrfs - Specific filesystems

**Networking:**
- networking - Network stack
- ipv4, ipv6 - Protocol implementations

**Drivers:**
- gpu, usb, pci - Device drivers

**Architecture:**
- x86, arm64 - Architecture-specific code

...and more! Use the Librarian to discover all available subdomains.

## Next Steps

1. Run the test suite to verify everything works
2. Try the example queries in interactive mode
3. Explore different subdomains
4. Customize configuration for your needs
5. Integrate into your own tools/workflows

For more details, see [README.md](README.md)
