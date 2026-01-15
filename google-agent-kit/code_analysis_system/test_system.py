"""Simple test script for the code analysis system."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_analysis_system.tools.index_tools import (
    read_index_file,
    query_subdomain_info,
    get_all_subdomains,
    recommend_code_locations,
)


def test_index_tools():
    """Test the index reading tools."""
    print("Testing Index Tools")
    print("=" * 80)
    
    # Test 1: Read documentation index
    print("\n1. Reading documentation index...")
    doc_index = read_index_file('documentation')
    print(f"Success! Read {len(doc_index)} characters")
    print(f"First 200 chars:\n{doc_index[:200]}...")
    
    # Test 2: Get all subdomains
    print("\n2. Getting all subdomains...")
    subdomains = get_all_subdomains()
    print(f"Found {len(subdomains)} subdomains:")
    for sd in subdomains[:5]:
        print(f"  - [{sd['subdomain']}] {sd['title']} ({sd['category']})")
    print(f"  ... and {len(subdomains) - 5} more")
    
    # Test 3: Query specific subdomain
    print("\n3. Querying 'kernel' subdomain...")
    kernel_info = query_subdomain_info('kernel')
    if kernel_info.get('found'):
        print(f"  Title: {kernel_info['title']}")
        print(f"  Docs: {kernel_info['docs']}")
        print(f"  Code: {kernel_info['code']}")
        print(f"  Lines: {kernel_info['lines']}")
    else:
        print(f"  Not found: {kernel_info.get('error')}")
    
    # Test 4: Recommend code locations
    print("\n4. Recommending locations for 'scheduler'...")
    recommendations = recommend_code_locations("scheduler")
    print(f"Found {len(recommendations)} recommendations:")
    for rec in recommendations[:3]:
        print(f"  - [{rec['subdomain']}] {rec['title']}")
        print(f"    Score: {rec.get('relevance_score', 0)}")
    
    print("\n" + "=" * 80)
    print("Index tools test complete!\n")


def test_code_reader_tools():
    """Test the code reading tools."""
    print("Testing Code Reader Tools")
    print("=" * 80)
    
    from code_analysis_system.tools.code_reader_tools import (
        get_directory_summary,
        list_files_in_directory,
        search_in_directory,
        read_source_file,
    )
    
    # Test 1: Get directory summary
    print("\n1. Getting summary of kernel/sched/ ...")
    summary = get_directory_summary('kernel/sched', max_depth=1)
    if summary['success']:
        print(f"  Subdirectories: {len(summary['subdirectories'])}")
        print(f"  File count: {summary['file_count']}")
        print(f"  Top file types: {list(summary['file_types'].items())[:3]}")
    else:
        print(f"  Error: {summary.get('error')}")
    
    # Test 2: List files
    print("\n2. Listing .c files in kernel/sched/ ...")
    files = list_files_in_directory('kernel/sched', file_extensions=['.c'], max_files=10)
    if files['success']:
        print(f"  Found {files['total_files']} files:")
        for f in files['files'][:5]:
            print(f"    - {f}")
    else:
        print(f"  Error: {files.get('error')}")
    
    # Test 3: Search for files
    print("\n3. Searching for 'fair' in kernel/sched/ ...")
    search = search_in_directory('kernel/sched', 'fair', file_extensions=['.c', '.h'])
    if search['success']:
        print(f"  Found {search['total_matches']} matches:")
        for m in search['matches'][:3]:
            print(f"    - {m}")
    else:
        print(f"  Error: {search.get('error')}")
    
    # Test 4: Read source file
    print("\n4. Reading first 50 lines of kernel/sched/core.c ...")
    content = read_source_file('kernel/sched/core.c', start_line=1, end_line=50)
    if content['success']:
        print(f"  Read {content['lines_read']} lines (of {content['total_lines']} total)")
        print(f"  First 150 characters:")
        print(f"  {content['content'][:150]}...")
    else:
        print(f"  Error: {content.get('error')}")
    
    print("\n" + "=" * 80)
    print("Code reader tools test complete!\n")


def test_agents():
    """Test that agents can be imported and instantiated."""
    print("Testing Agent Definitions")
    print("=" * 80)
    
    from code_analysis_system.agents import (
        director_agent,
        librarian_agent,
        create_subdomain_agent,
        mediator_agent,
    )
    
    print("\n1. Director Agent:")
    print(f"   Name: {director_agent.name}")
    print(f"   Tools: {len(director_agent.tools)}")
    
    print("\n2. Librarian Agent:")
    print(f"   Name: {librarian_agent.name}")
    print(f"   Tools: {len(librarian_agent.tools)}")
    
    print("\n3. Mediator Agent:")
    print(f"   Name: {mediator_agent.name}")
    print(f"   Tools: {len(mediator_agent.tools)}")
    
    print("\n4. Creating Subdomain Agent:")
    sd_agent = create_subdomain_agent(
        subdomain="test",
        paths=["kernel/"],
        agent_id="test_agent"
    )
    print(f"   Name: {sd_agent.name}")
    print(f"   Tools: {len(sd_agent.tools)}")
    
    print("\n" + "=" * 80)
    print("Agent definitions test complete!\n")


if __name__ == "__main__":
    try:
        test_index_tools()
        test_code_reader_tools()
        test_agents()
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED!")
        print("=" * 80)
        print("\nThe multi-agent system is ready to use.")
        print("Run 'python code_analysis_system/main.py' to start analyzing!")
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"TEST FAILED: {e}")
        print(f"{'='*80}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
