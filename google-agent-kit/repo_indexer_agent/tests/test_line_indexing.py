"""Test script to verify line-based indexing implementation"""
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import directly from tools to avoid loading agent module
from tools.repo_scanner import scan_and_analyze_repository
from tools.index_saver import save_all_indexes


def test_indexing():
    """Test the line-based indexing on the repo_indexer_agent directory itself"""
    
    # Test on a smaller directory first
    test_dir = Path(__file__).parent.parent
    
    print(f"Testing indexing on: {test_dir}")
    print("-" * 80)
    
    # Scan the repository
    print("Scanning repository...")
    result = scan_and_analyze_repository(
        root_path=str(test_dir),
        repo_name="repo_indexer_agent_test"
    )
    
    if result.get("status") == "error":
        print(f"ERROR: {result.get('message')}")
        return
    
    print(f"Status: {result.get('status')}")
    print(f"Total files: {result.get('total_files')}")
    print(f"Total directories: {result.get('total_directories')}")
    print(f"Total lines: {result.get('total_lines'):,}")
    print()
    
    # Save indexes
    print("Saving indexes...")
    output_dir = Path(__file__).parent.parent / "outputs" / "test_indexes"
    save_result = save_all_indexes(
        index_data=result,
        output_dir=str(output_dir),
        repo_name="test_repo"
    )
    
    if save_result.get("status") == "success":
        print(f"SUCCESS: {save_result.get('message')}")
        print("\nGenerated files:")
        for index_type, info in save_result.get('files', {}).items():
            print(f"  {index_type}: {info['path']} ({info['size']} bytes)")
    else:
        print(f"ERROR: {save_result.get('message')}")


if __name__ == "__main__":
    test_indexing()
