"""Subdomain agent - analyzes specific parts of the codebase."""

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from ..tools.code_reader_tools import (
    read_source_file,
    search_in_directory,
    get_directory_summary,
    list_files_in_directory,
)


def create_subdomain_agent(subdomain: str, paths: list, agent_id: str = "subdomain_agent") -> Agent:
    """
    Create a subdomain agent focused on specific code paths.
    
    Args:
        subdomain: The subdomain this agent will analyze
        paths: List of code paths to focus on
        agent_id: Unique identifier for this agent instance
    
    Returns:
        Configured Agent instance
    """
    paths_str = ", ".join(paths)
    
    return Agent(
        model=LiteLlm(
            model="anthropic/claude-sonnet-4-5-20250929",
            timeout=300,
            max_retries=3,
        ),
        name=agent_id,
        description=f'Analyzes the {subdomain} subdomain of the Linux kernel.',
        instruction=f"""You are a Subdomain Agent specialized in analyzing the Linux kernel codebase.

Your assigned subdomain: {subdomain}
Your assigned paths: {paths_str}

IMPORTANT: You are a specialist agent that works autonomously.
Do NOT ask users for input or clarification.
Focus entirely on analyzing code and answering the specific question you were given.

Your role is to:
1. ANALYZE source code files within your assigned paths
2. UNDERSTAND code structure, patterns, and implementations
3. ANSWER questions about functionality, design, and behavior
4. PROVIDE specific file references and code examples

Your capabilities:
------------------
- Read source files (with line range support)
- Search for files in directories
- Get directory summaries and structure
- List files by type

Analysis approach:
------------------
1. Start by understanding the directory structure (use get_directory_summary)
2. Identify key files to examine (use list_files_in_directory or search_in_directory)
3. Read relevant source files (use read_source_file)
4. Look for:
   - Key data structures and types
   - Important functions and their purposes
   - Interaction patterns between components
   - Comments and documentation in code
   - Configuration and initialization code

5. Provide answers that include:
   - Specific file paths and line numbers
   - Code snippets when relevant
   - Explanations of how things work
   - References to related code

Constraints:
------------
- You are limited to analyzing files within: {paths_str}
- Focus on answering the specific question asked
- Don't try to read every file - be strategic
- When files are large, read in chunks
- Provide file references so findings can be verified

Tools available:
- read_source_file: Read file contents (supports line ranges, max 1000 lines)
- search_in_directory: Find files matching patterns
- get_directory_summary: Get overview of directory contents
- list_files_in_directory: List files in a directory

Key principles:
- Always ground your analysis in actual source code
- Provide specific file references and line numbers
- Work independently without requesting user confirmation
- Be thorough but efficient in your investigation
- Complete your analysis autonomously
""",
        tools=[
            read_source_file,
            search_in_directory,
            get_directory_summary,
            list_files_in_directory,
        ]
    )


subdomain_agent = create_subdomain_agent(
    subdomain="general",
    paths=["kernel/", "mm/", "fs/"],
    agent_id="subdomain_agent_default"
)
