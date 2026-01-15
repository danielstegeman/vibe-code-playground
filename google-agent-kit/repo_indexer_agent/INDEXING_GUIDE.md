# Line-Based Repository Indexing System

## Overview

The repository indexing system has been overhauled to provide line-based metrics instead of byte-based sizes. It generates three complementary index formats optimized for different use cases.

## Key Changes

- **Line Counting**: All metrics now based on total lines per file/folder (not bytes)
- **Complete Hierarchy**: Shows ALL folders/files without filtering or thresholds
- **Token Optimization**: Hierarchical tree format minimizes tokens while preserving complete structure
- **Dual Index System**: Separate indexes for structure navigation and documentation mapping

## Generated Indexes

### 1. Hierarchical Index (`*_hierarchy.txt`)
**Purpose**: Token-optimized complete directory structure for agent navigation

**Format**:
```
linux/ (28,456,789)
├─ arch/ (4,234,567)
│  ├─ x86/ (1,456,789)
│  │  ├─ kernel/ (234,567)
│  │  └─ mm/ (123,456)
│  └─ arm/ (987,654)
├─ drivers/ (8,765,432)
└─ fs/ (2,456,789)
```

**Use Case**: Quickly understand repository structure and identify code-heavy subsystems

### 2. Summary Index (`*_summary.txt`)
**Purpose**: Statistical overview with file type distribution

**Includes**:
- Total files, directories, and lines of code
- File type distribution with percentages
- Top 10 files by line count
- Maximum directory depth

**Use Case**: High-level repository analysis and metrics

### 3. Documentation Subdomain Guide (`*_documentation_guide.txt`)
**Purpose**: Agent navigation for finding relevant code subsystems

**Format**:
```
[kernel] Process Management & Scheduling
  Docs: Documentation/scheduler/
  Code: kernel/sched/, include/linux/sched/
  Lines: ~456,789 LOC
```

**Use Case**: Map documentation topics to code locations for agent exploration

## Usage

### With ADK CLI
```bash
# Run the indexer agent
cd google-agent-kit
adk run repo_indexer_agent --use_local_storage

# The agent will:
# 1. Clone or verify existing repository
# 2. Scan and count lines
# 3. Generate all three index files
```

### Programmatic Usage
```python
from repo_indexer_agent.tools import (
    scan_and_analyze_repository,
    save_all_indexes
)

# Scan repository
result = scan_and_analyze_repository(
    root_path="/path/to/repo",
    repo_name="my-repo"
)

# Save all index formats
save_all_indexes(
    index_data=result,
    output_dir="./outputs/indexes",
    repo_name="my-repo"
)
```

## Line Counting Details

- **All Files**: Counts total lines in all text files
- **Binary Files**: Binary/unreadable files counted as 0 lines
- **No Filtering**: All code accounted for, no minimum threshold
- **Error Handling**: Permission errors or unreadable files are skipped

## Output Files

For a repository named `linux`, the following files are generated:
- `linux_hierarchy.txt` - Complete tree structure
- `linux_summary.txt` - Statistics and metrics  
- `linux_documentation_guide.txt` - Navigation guide

## Performance

- **Scanning**: Slower than byte-based (reads files) but still efficient
- **Large Repos**: Linux kernel (~90K files) scans in ~2-5 minutes
- **Memory**: Efficient - only stores metadata, not file contents
- **Disk**: Minimal - text files typically <5MB even for huge repos

## Token Optimization

The hierarchical index is designed to minimize token usage:
- Uses compact symbols: `├─ └─ │`
- Shows complete structure without truncation
- Line counts in parentheses: `folder/ (123,456)`
- Forward slashes for consistency across platforms

## Example Output

See the test indexes in `outputs/test_indexes/` for examples of each format.
