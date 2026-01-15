# Linux Kernel Code Analysis System

A multi-agent system for analyzing the Linux kernel codebase using AI agents.

## Architecture

The system uses 4 specialized agents working together:

1. **Director Agent** - Orchestrates the analysis workflow
   - Receives user queries
   - Creates analysis plans
   - Coordinates other agents
   - Manages workload distribution

2. **Librarian Agent** - Provides code location guidance
   - Consults pre-generated indexes
   - Recommends relevant subdomains
   - Provides LOC estimates
   - Maps queries to code paths

3. **Subdomain Agent(s)** - Analyzes specific code areas
   - Reads source files
   - Extracts relevant information
   - Provides file references
   - Can be dynamically spawned based on LOC limits

4. **Mediator Agent** - Synthesizes findings
   - Aggregates subdomain results
   - Identifies gaps
   - Requests additional analysis if needed
   - Formats final answers

## Workflow

```
User Query
    ↓
Director (plan)
    ↓
Librarian (identify locations)
    ↓
Director (allocate subdomain agents)
    ↓
Subdomain Agent(s) (analyze code) ← can spawn multiple based on LOC
    ↓
Mediator (synthesize answer)
    ↓
User Response
```

## Prerequisites

1. **Repository Indexes** - Generate indexes first:
   ```bash
   cd google-agent-kit
   python repo_indexer_agent/tests/generate_linux_indexes.py
   ```

2. **Linux Kernel Repository** - Ensure `linux_repo/` exists with the kernel source

3. **API Key** - Set `ANTHROPIC_API_KEY` in `.env` file

## Usage

### Command Line

```bash
cd google-agent-kit/code_analysis_system
python main.py
```

Then enter queries like:
- "How does the Linux scheduler work?"
- "Explain memory management in Linux"
- "What is the VFS layer?"

### Programmatic

```python
from code_analysis_system.orchestrator import run_analysis

answer = run_analysis(
    "How does the Linux scheduler work?",
    max_lines_per_agent=100000
)
print(answer)
```

## Configuration

Edit [config.py](config.py) to customize:

- `MAX_LINES_PER_SUBDOMAIN_AGENT` - LOC limit per agent (default: 100,000)
- `MAX_FILE_READ_LINES` - Max lines to read from a file (default: 1,000)
- `MODEL_NAME` - LLM model to use
- `MODEL_TIMEOUT` - Request timeout in seconds

## Tools

### Index Tools (Librarian)
- `read_index_file()` - Read hierarchy/summary/documentation indexes
- `query_subdomain_info()` - Get details about a subdomain
- `get_all_subdomains()` - List all available subdomains
- `recommend_code_locations()` - Get ranked location recommendations

### Code Reader Tools (Subdomain Agents)
- `read_source_file()` - Read file contents with line ranges
- `search_in_directory()` - Find files matching patterns
- `get_directory_summary()` - Get directory overview
- `list_files_in_directory()` - List files in a directory

### Routing Tools (Director/Mediator)
- `create_subdomain_context()` - Split subdomains by LOC limits
- `aggregate_agent_responses()` - Combine findings from multiple agents
- `format_agent_handoff()` - Format handoff messages

## Project Structure

```
code_analysis_system/
├── agents/
│   ├── director.py       # Director agent definition
│   ├── librarian.py      # Librarian agent definition
│   ├── subdomain.py      # Subdomain agent factory
│   └── mediator.py       # Mediator agent definition
├── tools/
│   ├── index_tools.py    # Index reading and querying
│   ├── code_reader_tools.py  # Source code reading
│   └── routing_tools.py  # Agent coordination
├── orchestrator.py       # Main orchestration logic
├── config.py            # Configuration settings
├── main.py              # CLI entry point
└── README.md            # This file
```

## How It Works

### Phase 1: Planning
Director receives the query and creates an analysis plan by understanding what needs to be investigated.

### Phase 2: Location Discovery
Librarian consults the documentation index to identify relevant subdomains and code paths. Returns LOC estimates for each area.

### Phase 3: Agent Allocation
Director decides how many Subdomain Agents are needed based on:
- Total LOC to analyze
- `MAX_LINES_PER_SUBDOMAIN_AGENT` limit
- Complexity of the query

### Phase 4: Code Analysis
Each Subdomain Agent:
- Focuses on its assigned paths
- Reads relevant source files
- Extracts key information
- Provides file references

### Phase 5: Synthesis
Mediator:
- Aggregates findings from all agents
- Identifies gaps or conflicts
- Requests additional analysis if needed
- Formats the final answer

## Example

**Query:** "How does the Linux scheduler work?"

1. **Director** creates plan to investigate process scheduling
2. **Librarian** recommends `[kernel]` subdomain → `kernel/sched/` (~65,958 LOC)
3. **Director** allocates 1 Subdomain Agent (within 100K limit)
4. **Subdomain Agent** analyzes:
   - `kernel/sched/core.c` - Main scheduler code
   - `kernel/sched/fair.c` - CFS implementation
   - `include/linux/sched.h` - Task structures
5. **Mediator** synthesizes answer explaining scheduler architecture with file references

## Future Enhancements

- [ ] Parallel subdomain agent execution
- [ ] Caching of analyzed files
- [ ] Interactive refinement of answers
- [ ] Support for multiple repositories
- [ ] Web interface
- [ ] Query history and learning
