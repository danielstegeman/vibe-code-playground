"""Main entry point for the Linux codebase analysis system."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_analysis_system.orchestrator import run_analysis


def main():
    """Main entry point for command-line usage."""
    print("="*80)
    print("Linux Kernel Code Analysis System")
    print("Multi-Agent Architecture: Director → Librarian → Subdomain → Mediator")
    print("="*80)
    
    # Example queries
    example_queries = [
        "How does the Linux scheduler work?",
        "What is the memory management subsystem responsible for?",
        "How does the VFS layer interact with specific filesystems?",
        "Explain the network stack architecture in Linux",
    ]
    
    print("\nExample queries:")
    for i, q in enumerate(example_queries, 1):
        print(f"{i}. {q}")
    
    print("\nEnter your query (or 'q' to quit):")
    
    while True:
        query = input("\n> ").strip()
        
        if query.lower() in ('q', 'quit', 'exit'):
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            # Run the analysis
            answer = run_analysis(query, max_lines_per_agent=100000)
            
            print("\n" + "="*80)
            print("FINAL ANSWER")
            print("="*80)
            print(answer)
            print("\n" + "="*80)
            
        except KeyboardInterrupt:
            print("\n\nAnalysis interrupted.")
            break
        except Exception as e:
            print(f"\nError during analysis: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
