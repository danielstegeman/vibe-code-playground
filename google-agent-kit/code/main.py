"""
Main orchestration script for the repository indexing agent.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import repo_indexer_agent
sys.path.insert(0, str(Path(__file__).parent.parent))

from repo_indexer_agent import indexer_agent


async def index_linux_kernel():
    """Index the Linux kernel repository."""
    
    print("=" * 80)
    print("Linux Kernel Repository Indexer")
    print("=" * 80)
    print()
    
    # Configuration
    repo_url = "https://github.com/torvalds/linux.git"
    repo_name = "linux-kernel"
    clone_dir = Path(__file__).parent.parent / "cloned_repos" / repo_name
    output_dir = Path(__file__).parent.parent / "outputs" / "indexes"
    output_file = output_dir / f"{repo_name}_index.txt"
    
    print(f"Repository URL: {repo_url}")
    print(f"Clone directory: {clone_dir}")
    print(f"Output file: {output_file}")
    print()
    
    # Prepare the indexing request
    request = f"""Please index the Linux kernel repository with the following parameters:

Repository URL: {repo_url}
Clone to directory: {clone_dir}
Use shallow clone: yes (for faster cloning)

After cloning:
1. Scan the entire directory structure
2. Analyze file distributions by type and location
3. Calculate statistics on the repository organization
4. Generate a comprehensive index report
5. Save the report to: {output_file}

Please provide progress updates as you work through these steps."""
    
    print("Sending request to indexer agent...")
    print("-" * 80)
    print()
    
    try:
        # Run the agent (streaming response)
        print()
        print("-" * 80)
        print("Agent Response:")
        print("-" * 80)
        
        full_response = []
        async for chunk in indexer_agent.run_async(request):
            if hasattr(chunk, 'content'):
                content = chunk.content
                print(content, end='', flush=True)
                full_response.append(content)
            elif isinstance(chunk, str):
                print(chunk, end='', flush=True)
                full_response.append(chunk)
        
        print()
        print()
        
        # Check if output file was created
        if output_file.exists():
            size_kb = output_file.stat().st_size / 1024
            print(f"✓ Index file created: {output_file} ({size_kb:.2f} KB)")
        else:
            print("✗ Index file was not created")
            
    except Exception as e:
        print(f"Error running indexer agent: {e}")
        raise
    
    print()
    print("=" * 80)
    print("Indexing complete!")
    print("=" * 80)


async def index_custom_repository(repo_url: str, repo_name: str = None):
    """Index a custom repository."""
    
    if repo_name is None:
        # Extract repo name from URL
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    
    print(f"\nIndexing repository: {repo_url}")
    print(f"Repository name: {repo_name}\n")
    
    clone_dir = Path(__file__).parent.parent / "cloned_repos" / repo_name
    output_dir = Path(__file__).parent.parent / "outputs" / "indexes"
    output_file = output_dir / f"{repo_name}_index.txt"
    
    request = f"""Index this repository:

Repository URL: {repo_url}
Clone to: {clone_dir}
Output file: {output_file}

Perform a complete analysis and save the results."""
    
    async for chunk in indexer_agent.run_async(request):
        if hasattr(chunk, 'content'):
            print(chunk.content, end='', flush=True)
        elif isinstance(chunk, str):
            print(chunk, end='', flush=True)
    print()


async def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        # Custom repository provided via command line
        repo_url = sys.argv[1]
        repo_name = sys.argv[2] if len(sys.argv) > 2 else None
        await index_custom_repository(repo_url, repo_name)
    else:
        # Default: index Linux kernel
        await index_linux_kernel()


if __name__ == "__main__":
    asyncio.run(main())
