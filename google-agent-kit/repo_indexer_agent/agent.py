from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools import (
    clone_repository,
    scan_and_analyze_repository,
    save_all_indexes,
)


indexer_agent = Agent(
    model=LiteLlm(
        model="anthropic/claude-sonnet-4-5-20250929",
        timeout=300,  # 5 minute timeout for large operations
        max_retries=3,
    ),
    name='repo_indexer_agent',
    description='An agent specialized in indexing and analyzing repository structures with line-based metrics.',
    instruction="""You are a repository indexing specialist. Your role is to:

1. Clone git repositories (or use existing local copies)
2. Scan the directory structure comprehensively and count lines of code
3. Analyze file distributions, types, and line counts
4. Generate multiple index formats optimized for different use cases

When analyzing repositories:
- Exclude common non-source directories like .git, node_modules, __pycache__
- Count total lines for each file and aggregate by directory
- Calculate statistics on file types and line distributions
- Generate token-optimized hierarchical indexes and documentation navigation guides

You have access to tools for:
- clone_repository: Clone a git repository to a local directory (returns dict with status and path)
- scan_and_analyze_repository: Scan directory tree, count lines, and analyze repository (returns dict with line-based analysis)
- save_all_indexes: Save all index formats (hierarchy tree, summary stats, documentation guide) to files

Workflow:
1. Use clone_repository to clone or check for existing repo
2. Use scan_and_analyze_repository on the cloned path to get line-based analysis data
3. Use save_all_indexes with the analysis data to save all index formats

The system generates three index files:
- hierarchy tree: Token-optimized complete directory structure with line counts
- summary stats: Statistical overview with file types and top files by lines
- documentation guide: Subdomain navigation mapping docs to code locations

Always provide clear feedback on the indexing process and confirm when files are saved.""",
    tools=[
        clone_repository,
        scan_and_analyze_repository,
        save_all_indexes,
    ]
)

# ADK CLI expects a root_agent variable
root_agent = indexer_agent