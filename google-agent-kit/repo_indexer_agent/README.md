# Repository Indexer Agent

A specialized agent for indexing and analyzing repository structures, built with Google Agent Development Kit (ADK).

## Overview

This agent is part of a multi-agent system designed to analyze the Linux kernel codebase. The Repository Indexer is the first agent in the pipeline, responsible for:

- Cloning git repositories (or using existing local copies)
- Scanning directory structures comprehensively
- Analyzing file distributions by type, size, and location
- Generating detailed index reports in plain text format

## Structure

```
repo_indexer_agent/
├── __init__.py           # Agent module exports
├── agent.py              # Agent definition and configuration
└── tools/                # Agent tools
    ├── __init__.py
    ├── data_models.py    # Pydantic models for structured data
    ├── repo_scanner.py   # Repository cloning and scanning logic
    └── output_formatter.py  # Output formatting and file saving
```

## Features

### Tools Available

1. **clone_repository**: Clone git repositories with optional shallow cloning
2. **scan_directory_structure**: Recursively scan directory trees with configurable depth
3. **analyze_file_distribution**: Analyze files and create comprehensive repository index
4. **save_index_to_file**: Save index reports to plain text files

### Index Report Includes

- Total file and directory counts
- Total repository size
- File type distribution with percentages
- Largest files (top 50 tracked, top 10 displayed)
- Directory statistics (files, subdirs, size per directory)
- Maximum depth level of directory tree

## Usage

### Index the Linux Kernel (Default)

```bash
cd google-agent-kit
python code/main.py
```

### Index a Custom Repository

```bash
python code/main.py <repository-url> [repository-name]
```

Example:
```bash
python code/main.py https://github.com/python/cpython.git cpython
```

## Output

Index reports are saved to `outputs/indexes/` as plain text files:

- `outputs/indexes/linux-kernel_index.txt` - Linux kernel index
- `outputs/indexes/<repo-name>_index.txt` - Custom repository indexes

Cloned repositories are stored in:
- `cloned_repos/<repo-name>/`

## Configuration

The agent uses:
- **Model**: Claude Sonnet 4.5 via LiteLLM
- **Shallow cloning**: Enabled by default (depth=1) for faster cloning
- **Excluded directories**: `.git`, `node_modules`, `__pycache__`, `.venv`, `venv`

## Next Steps

This indexer agent is the foundation for a multi-agent system. Future agents will:

- Analyze code patterns and architecture
- Review security vulnerabilities
- Generate documentation
- Perform quality analysis

## Requirements

- Python 3.8+
- Google ADK installed
- Git installed on system
- Anthropic API key in `.env` file
