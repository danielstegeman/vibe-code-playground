"""Generate indexes for the Linux kernel repository"""
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import directly from tools to avoid loading agent module
from tools.repo_scanner import scan_and_analyze_repository
from tools.index_saver import save_all_indexes


def generate_linux_indexes():
    """Generate all index formats for the Linux kernel repository"""
    
    linux_repo = Path(__file__).parent.parent.parent / "linux_repo"
    
    if not linux_repo.exists():
        print(f"ERROR: Linux repository not found at {linux_repo}")
        print("Please ensure the Linux kernel repo is cloned first.")
        return
    
    print(f"Indexing Linux kernel repository: {linux_repo}")
    print("=" * 80)
    print("This may take several minutes for a large repository...")
    print()
    
    # Scan the repository
    print("[1/2] Scanning repository and counting lines...")
    print("      - Walking directory tree")
    print("      - Counting lines in each file")
    print("      - Aggregating statistics")
    
    result = scan_and_analyze_repository(
        root_path=str(linux_repo),
        repo_url="https://github.com/torvalds/linux",
        repo_name="linux"
    )
    
    if result.get("status") == "error":
        print(f"      ✗ ERROR: {result.get('message')}")
        return
    
    print(f"      ✓ Scan complete!")
    print(f"        Files scanned: {result.get('total_files'):,}")
    print(f"        Directories: {result.get('total_directories'):,}")
    print(f"        Total lines: {result.get('total_lines'):,}")
    print(f"        Max depth: {result.get('max_depth')}")
    print()
    
    # Save all indexes
    print("[2/2] Generating index files...")
    output_dir = Path(__file__).parent.parent.parent / "outputs" / "indexes"
    print(f"      Output directory: {output_dir}")
    print()
    print("      - Creating hierarchy tree index...")
    print("      - Creating summary statistics index...")
    print("      - Creating documentation subdomain guide...")
    
    save_result = save_all_indexes(
        index_data=result,
        output_dir=str(output_dir),
        repo_name="linux"
    )
    
    if save_result.get("status") == "success":
        print(f"      ✓ All indexes generated successfully!")
        print()
        print("=" * 80)
        print("GENERATED INDEX FILES")
        print("=" * 80)
        
        index_descriptions = {
            'hierarchy': 'Complete directory tree with LOC counts',
            'summary': 'Statistical overview and file types',
            'documentation': 'Agent navigation guide for code domains'
        }
        
        for index_type, info in save_result.get('files', {}).items():
            size_kb = info['size'] / 1024
            filename = Path(info['path']).name
            description = index_descriptions.get(index_type, '')
            print(f"\n  [{index_type.upper()}]")
            print(f"    File: {filename}")
            print(f"    Size: {size_kb:.1f} KB")
            print(f"    Desc: {description}")
        
        print()
        print("=" * 80)
    else:
        print(f"      ✗ ERROR: {save_result.get('message')}")


if __name__ == "__main__":
    generate_linux_indexes()
