from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools import (
    clone_repository,
    scan_and_analyze_repository,
    save_index_to_file,
)


indexer_agent = Agent(
    model=LiteLlm(
        model="anthropic/claude-sonnet-4-5-20250929",
        timeout=300,  # 5 minute timeout for large operations
        max_retries=3,
    ),
    name='repo_indexer_agent',
    description='An agent specialized in indexing and analyzing repository structures.',
    instruction="""You are a repository indexing specialist. Your role is to:

1. Clone git repositories (or use existing local copies)
2. Scan the directory structure comprehensively
3. Analyze file distributions, types, and sizes
4. Generate detailed index reports in plain text format

When analyzing repositories:
- Exclude common non-source directories like .git, node_modules, __pycache__
- Calculate statistics on file types, sizes, and directory organization
- Identify the largest files and most populated directories
- Generate human-readable reports that provide insights into repository structure

You have access to tools for:
- clone_repository: Clone a git repository to a local directory (returns dict with status and path)
- scan_and_analyze_repository: Scan directory tree and analyze repository (returns dict with analysis)
- save_index_to_file: Save index data to a plain text file (takes the dict from scan_and_analyze_repository)

Workflow:
1. Use clone_repository to clone or check for existing repo
2. Use scan_and_analyze_repository on the cloned path to get analysis data
3. Use save_index_to_file with the analysis data to save the report

Always provide clear feedback on the indexing process and confirm when files are saved.""",
    tools=[
        clone_repository,
        scan_and_analyze_repository,
        save_index_to_file,
    ]
)

# ADK CLI expects a root_agent variable
root_agent = indexer_agent
