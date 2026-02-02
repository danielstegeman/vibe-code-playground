# Multi-Agent System Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                  (CLI: main.py or Programmatic API)                 │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                │ Query: "How does Linux scheduler work?"
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CODE ANALYSIS ORCHESTRATOR                      │
│                        (orchestrator.py)                            │
│                                                                     │
│  Manages 5-Phase Workflow:                                         │
│  1. Director Planning                                              │
│  2. Librarian Location Discovery                                   │
│  3. Director Agent Allocation                                      │
│  4. Subdomain Code Analysis                                        │
│  5. Mediator Synthesis                                             │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │                       │
                    ▼                       ▼
        ┌───────────────────┐   ┌──────────────────┐
        │  PHASE 1 & 3      │   │  PHASE 2         │
        │  DIRECTOR AGENT   │   │  LIBRARIAN AGENT │
        │  (director.py)    │   │  (librarian.py)  │
        │                   │   │                  │
        │  Responsibilities:│   │  Responsibilities:
        │  • Plan analysis  │   │  • Read indexes  │
        │  • Coordinate     │   │  • Query domains │
        │  • Allocate work  │   │  • Recommend     │
        │                   │   │    locations     │
        │  Tools:           │   │                  │
        │  • create_        │   │  Tools:          │
        │    subdomain_     │   │  • read_index_   │
        │    context        │   │    file          │
        │  • format_agent_  │   │  • query_        │
        │    handoff        │   │    subdomain_info│
        └─────────┬─────────┘   │  • get_all_      │
                  │             │    subdomains    │
                  │             │  • recommend_    │
                  │             │    code_locations│
                  │             └────────┬─────────┘
                  │                      │
                  │                      │ Consults
                  │                      ▼
                  │             ┌─────────────────────┐
                  │             │   REPOSITORY        │
                  │             │   INDEXES           │
                  │             │                     │
                  │             │  • Hierarchical     │
                  │             │    Index (tree)     │
                  │             │  • Summary Stats    │
                  │             │  • Documentation    │
                  │             │    Guide (subdomains)│
                  │             └─────────────────────┘
                  │
                  │ Creates based on LOC limits
                  ▼
        ┌──────────────────────────────────────┐
        │     PHASE 4: SUBDOMAIN AGENTS        │
        │     (subdomain.py - dynamic)         │
        │                                      │
        │  ┌──────────┐  ┌──────────┐        │
        │  │ Agent 1  │  │ Agent 2  │  ...   │
        │  │          │  │          │        │
        │  │ Paths:   │  │ Paths:   │        │
        │  │ kernel/  │  │ mm/      │        │
        │  │ sched/   │  │          │        │
        │  │          │  │          │        │
        │  │ ~65K LOC │  │ ~80K LOC │        │
        │  └────┬─────┘  └────┬─────┘        │
        │       │             │              │
        │       │ Tools:      │              │
        │       │ • read_source_file         │
        │       │ • search_in_directory      │
        │       │ • get_directory_summary    │
        │       │ • list_files_in_directory  │
        └───────┴─────────────┴──────────────┘
                │             │
                │ Findings    │ Findings
                ▼             ▼
        ┌─────────────────────────────────┐
        │     PHASE 5: MEDIATOR AGENT     │
        │        (mediator.py)            │
        │                                 │
        │  Responsibilities:              │
        │  • Aggregate findings           │
        │  • Identify gaps                │
        │  • Request more agents          │
        │  • Synthesize answer            │
        │                                 │
        │  Tools:                         │
        │  • aggregate_agent_responses    │
        └────────────┬────────────────────┘
                     │
                     │ Final Answer
                     ▼
        ┌─────────────────────────────────┐
        │         USER RECEIVES           │
        │    Comprehensive Answer with    │
        │    File References & Details    │
        └─────────────────────────────────┘
```

## Data Flow Diagram

```
┌────────┐
│  User  │
│ Query  │
└───┬────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 1. DIRECTOR: Formulate Plan                     │
│    Input:  User query                           │
│    Output: Analysis plan                        │
└───┬──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 2. LIBRARIAN: Identify Locations                │
│    Input:  Query + Plan                         │
│    Process:                                      │
│    • Read documentation index                   │
│    • Find relevant subdomains                   │
│    • Extract code paths & LOC                   │
│    Output: List of subdomains with paths & LOC  │
└───┬──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 3. DIRECTOR: Allocate Agents                    │
│    Input:  Subdomain recommendations            │
│    Process:                                      │
│    • Check LOC for each subdomain               │
│    • Calculate # agents needed                  │
│    • Split paths if LOC > limit                 │
│    Output: Agent allocation plan                │
└───┬──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 4. SUBDOMAIN AGENT(S): Analyze Code             │
│    Input:  Assigned paths & instructions        │
│    Process (per agent):                          │
│    • Get directory summary                      │
│    • Search for relevant files                  │
│    • Read source files (strategic)              │
│    • Extract information                        │
│    Output: Findings + file references           │
└───┬──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 5. MEDIATOR: Synthesize Answer                  │
│    Input:  All subdomain findings               │
│    Process:                                      │
│    • Aggregate responses                        │
│    • Resolve conflicts                          │
│    • Identify gaps                              │
│    • Format comprehensive answer                │
│    Output: Final answer                         │
└───┬──────────────────────────────────────────────┘
    │
    ▼
┌────────┐
│  User  │
│ Answer │
└────────┘
```

## Component Interaction Matrix

```
                        ┌─────────┬──────────┬──────────┬──────────┐
                        │Director │Librarian │Subdomain │ Mediator │
┌───────────────────────┼─────────┼──────────┼──────────┼──────────┤
│ Receives from User    │   ✓     │          │          │          │
├───────────────────────┼─────────┼──────────┼──────────┼──────────┤
│ Consults Indexes      │         │    ✓     │          │          │
├───────────────────────┼─────────┼──────────┼──────────┼──────────┤
│ Reads Source Code     │         │          │    ✓     │          │
├───────────────────────┼─────────┼──────────┼──────────┼──────────┤
│ Creates Agents        │   ✓     │          │          │          │
├───────────────────────┼─────────┼──────────┼──────────┼──────────┤
│ Aggregates Results    │         │          │          │    ✓     │
├───────────────────────┼─────────┼──────────┼──────────┼──────────┤
│ Sends to User         │         │          │          │    ✓     │
└───────────────────────┴─────────┴──────────┴──────────┴──────────┘

Communication Paths:
  User        → Director  (query)
  Director    → Librarian (plan)
  Librarian   → Director  (recommendations)
  Director    → Subdomain (assignments)
  Subdomain   → Mediator  (findings)
  Mediator   ↔ Director   (request more agents if needed)
  Mediator    → User      (final answer)
```

## Tool Distribution

```
┌─────────────────────────────────────────────────────────────┐
│                    TOOL CATEGORIES                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INDEX TOOLS (Librarian)                                    │
│  ┌────────────────────────────────────────────────┐        │
│  │ • read_index_file                              │        │
│  │ • query_subdomain_info                         │        │
│  │ • get_all_subdomains                           │        │
│  │ • recommend_code_locations                     │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
│  CODE READER TOOLS (Subdomain Agents)                       │
│  ┌────────────────────────────────────────────────┐        │
│  │ • read_source_file                             │        │
│  │ • search_in_directory                          │        │
│  │ • get_directory_summary                        │        │
│  │ • list_files_in_directory                      │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
│  ROUTING TOOLS (Director & Mediator)                        │
│  ┌────────────────────────────────────────────────┐        │
│  │ • create_subdomain_context      (Director)     │        │
│  │ • format_agent_handoff          (Director)     │        │
│  │ • aggregate_agent_responses     (Mediator)     │        │
│  │ • spawn_subdomain_agent         (Mediator)     │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## LOC-Based Work Distribution

```
                        Librarian Recommendation
                                 │
                                 │ subdomain: "networking"
                                 │ paths: "net/, drivers/net/"
                                 │ lines: ~23,262,841 LOC
                                 ▼
                        ┌─────────────────┐
                        │    Director     │
                        │  Calculates:    │
                        │  23M / 100K =   │
                        │  ~232 agents    │
                        └────────┬────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
         ┌───────────┐    ┌───────────┐   ┌───────────┐
         │  Agent 1  │    │  Agent 2  │...│ Agent 232 │
         │           │    │           │   │           │
         │ net/core/ │    │ net/ipv4/ │   │drivers/   │
         │           │    │           │   │net/...    │
         │ ~100K LOC │    │ ~100K LOC │   │ ~100K LOC │
         └───────────┘    └───────────┘   └───────────┘
```

## File Organization

```
code_analysis_system/
│
├── Core Files
│   ├── __init__.py              Package initialization
│   ├── config.py                Configuration & settings
│   ├── orchestrator.py          Main workflow logic
│   └── main.py                  CLI entry point
│
├── Agents (agents/)
│   ├── __init__.py
│   ├── director.py              Planning & coordination
│   ├── librarian.py             Index consultation
│   ├── subdomain.py             Code analysis (factory)
│   └── mediator.py              Synthesis & gap detection
│
├── Tools (tools/)
│   ├── __init__.py
│   ├── index_tools.py           Index reading & querying
│   ├── code_reader_tools.py     Source file reading
│   └── routing_tools.py         Agent communication
│
├── Documentation
│   ├── README.md                Full documentation
│   ├── QUICKSTART.md            Quick start guide
│   ├── IMPLEMENTATION_SUMMARY.md This summary
│   └── ARCHITECTURE.md          This file
│
└── Testing
    └── test_system.py           System tests
```

## State Management

```
┌─────────────────────────────────────────────────┐
│         AnalysisContext (orchestrator.py)       │
├─────────────────────────────────────────────────┤
│                                                 │
│  query: str                                     │
│    └─> The user's original question            │
│                                                 │
│  relevant_subdomains: List[Dict]                │
│    └─> Identified by Librarian                 │
│                                                 │
│  subdomain_agents: List[Agent]                  │
│    └─> Created by Director                     │
│                                                 │
│  findings: List[Dict]                           │
│    └─> Results from Subdomain Agents           │
│                                                 │
│  final_response: Optional[str]                  │
│    └─> Synthesized by Mediator                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│        Application Layer                │
│  • CLI Interface (main.py)              │
│  • Orchestrator (orchestrator.py)       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        Agent Layer                      │
│  • Google ADK Agent Framework           │
│  • 4 Specialized Agents                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        LLM Layer                        │
│  • LiteLLM (model routing)              │
│  • Claude Sonnet 4.5                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        Tool Layer                       │
│  • Index Tools                          │
│  • Code Reader Tools                    │
│  • Routing Tools                        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        Data Layer                       │
│  • Pre-generated Indexes                │
│  • Linux Kernel Repository              │
│  • File System                          │
└─────────────────────────────────────────┘
```

---
*Architecture documented January 13, 2026*
