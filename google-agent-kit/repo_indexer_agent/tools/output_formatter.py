from pathlib import Path
from typing import Dict, List, Set


def format_lines(lines: int) -> str:
    """Format line count to human-readable format with comma separators."""
    return f"{lines:,}"


def format_hierarchy_tree(index_data: dict) -> str:
    """
    Format repository index as a hierarchical tree with line counts.
    Optimized for minimal token usage while showing complete structure.
    
    Args:
        index_data: Dictionary with repository index data
        
    Returns:
        Formatted hierarchical tree string
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"{index_data.get('repository_name', 'REPOSITORY').upper()} - HIERARCHICAL INDEX")
    lines.append("=" * 80)
    lines.append(f"Indexed: {index_data.get('indexed_at', 'Unknown')[:19]}")
    total_files = index_data.get('total_files', 0)
    total_dirs = index_data.get('total_directories', 0)
    total_lines = index_data.get('total_lines', 0)
    lines.append(f"Total: {total_files:,} files | {total_dirs:,} dirs | {format_lines(total_lines)} LOC")
    lines.append("")
    
    # Build tree structure
    dir_hierarchy = index_data.get('directory_hierarchy', {})
    if not dir_hierarchy:
        lines.append("No directory data available")
        return "\n".join(lines)
    
    # Start with root
    root_name = index_data.get('repository_name', 'root')
    root_data = dir_hierarchy.get(".", {})
    root_lines = root_data.get('total_lines', total_lines)
    lines.append(f"{root_name}/ ({format_lines(root_lines)})")
    
    # Get all directories and sort
    all_dirs = sorted([path for path in dir_hierarchy.keys() if path != "."])
    
    # Build tree recursively
    def add_dir_to_tree(dir_path: str, prefix: str, is_last: bool, processed: Set[str]):
        if dir_path in processed:
            return
        processed.add(dir_path)
        
        dir_data = dir_hierarchy.get(dir_path, {})
        dir_name = Path(dir_path).name
        dir_lines = dir_data.get('total_lines', 0)
        
        # Draw tree branch
        branch = "└─" if is_last else "├─ "
        lines.append(f"{prefix}{branch}{dir_name}/ ({format_lines(dir_lines)})")
        
        # Get subdirectories
        subdirs = dir_data.get('subdirectories', [])
        if not subdirs:
            return
        
        # Prepare next level prefix
        next_prefix = prefix + ("   " if is_last else "│  ")
        
        # Sort subdirectories
        subdirs_sorted = sorted(subdirs)
        for i, subdir in enumerate(subdirs_sorted):
            subdir_path = f"{dir_path}/{subdir}" if dir_path != "." else subdir
            is_last_subdir = (i == len(subdirs_sorted) - 1)
            add_dir_to_tree(subdir_path, next_prefix, is_last_subdir, processed)
    
    # Process root-level directories
    root_subdirs = sorted(root_data.get('subdirectories', []))
    processed_dirs = set()
    
    for i, subdir in enumerate(root_subdirs):
        is_last = (i == len(root_subdirs) - 1)
        add_dir_to_tree(subdir, "", is_last, processed_dirs)
    
    lines.append("")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def format_index_to_text(index_data: dict) -> str:
    """
    Format repository index with summary statistics and file type distribution.
    
    Args:
        index_data: Dictionary with repository index data
        
    Returns:
        Formatted text string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("REPOSITORY INDEX REPORT")
    lines.append("=" * 80)
    lines.append(f"Repository: {index_data.get('repository_name', 'Unknown')}")
    if index_data.get('repository_url'):
        lines.append(f"URL: {index_data['repository_url']}")
    lines.append(f"Indexed at: {index_data.get('indexed_at', 'Unknown')}")
    lines.append("")
    
    lines.append("-" * 80)
    lines.append("SUMMARY STATISTICS")
    lines.append("-" * 80)
    lines.append(f"Total Files: {index_data.get('total_files', 0):,}")
    lines.append(f"Total Directories: {index_data.get('total_directories', 0):,}")
    lines.append(f"Total Lines of Code: {format_lines(index_data.get('total_lines', 0))}")
    lines.append(f"Maximum Depth: {index_data.get('max_depth', 0)}")
    lines.append("")
    
    # File type distribution
    file_type_dist = index_data.get('file_type_distribution', {})
    if file_type_dist:
        lines.append("-" * 80)
        lines.append("FILE TYPE DISTRIBUTION")
        lines.append("-" * 80)
        total_files = index_data.get('total_files', 0)
        sorted_types = sorted(file_type_dist.items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_types[:20]:
            percentage = (count / total_files * 100) if total_files > 0 else 0
            ext_display = ext if ext else "(no extension)"
            lines.append(f"{ext_display:20} {count:8,} files ({percentage:5.2f}%)")
        lines.append("")
    
    # Files with most lines
    files_by_lines = index_data.get('files_by_lines', [])
    if files_by_lines:
        lines.append("-" * 80)
        lines.append("FILES WITH MOST LINES (Top 10)")
        lines.append("-" * 80)
        for i, file_info in enumerate(files_by_lines[:10], 1):
            lines.append(f"{i:2}. {format_lines(file_info['lines']):>10} LOC - {file_info['path']}")
        lines.append("")
    
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def create_documentation_index(index_data: dict) -> str:
    """
    Create a documentation subdomain navigation index for agents.
    Maps documentation topics to relevant code subsystems.
    
    Args:
        index_data: Dictionary with repository index data
        
    Returns:
        Formatted documentation navigation guide
    """
    lines = []
    lines.append("=" * 80)
    lines.append("DOCUMENTATION SUBDOMAIN INDEX - AGENT NAVIGATION GUIDE")
    lines.append("=" * 80)
    lines.append("")
    
    dir_hierarchy = index_data.get('directory_hierarchy', {})
    
    # Define common documentation to code mappings for Linux kernel
    doc_mappings = [
        {
            "category": "CORE SUBSYSTEMS",
            "domains": [
                {
                    "name": "kernel",
                    "title": "Process Management & Scheduling",
                    "docs": ["Documentation/scheduler/", "Documentation/admin-guide/kernel-parameters.txt"],
                    "code": ["kernel/sched/", "include/linux/sched/"],
                },
                {
                    "name": "mm",
                    "title": "Memory Management",
                    "docs": ["Documentation/mm/", "Documentation/admin-guide/mm/"],
                    "code": ["mm/", "include/linux/mm*.h"],
                },
                {
                    "name": "locking",
                    "title": "Synchronization & Locking",
                    "docs": ["Documentation/locking/"],
                    "code": ["kernel/locking/", "include/linux/spinlock.h", "include/linux/mutex.h"],
                },
            ]
        },
        {
            "category": "FILESYSTEMS",
            "domains": [
                {
                    "name": "fs",
                    "title": "Virtual Filesystem Layer",
                    "docs": ["Documentation/filesystems/vfs.rst"],
                    "code": ["fs/*.c", "include/linux/fs.h"],
                },
                {
                    "name": "ext4",
                    "title": "EXT4 Filesystem",
                    "docs": ["Documentation/filesystems/ext4/"],
                    "code": ["fs/ext4/"],
                },
                {
                    "name": "btrfs",
                    "title": "Btrfs Filesystem",
                    "docs": ["Documentation/filesystems/btrfs.rst"],
                    "code": ["fs/btrfs/"],
                },
            ]
        },
        {
            "category": "NETWORKING",
            "domains": [
                {
                    "name": "networking",
                    "title": "Network Stack",
                    "docs": ["Documentation/networking/"],
                    "code": ["net/", "drivers/net/", "include/net/"],
                },
                {
                    "name": "ipv4",
                    "title": "IPv4 Protocol Implementation",
                    "docs": ["Documentation/networking/ip-sysctl.rst"],
                    "code": ["net/ipv4/"],
                },
                {
                    "name": "wireless",
                    "title": "Wireless Subsystem",
                    "docs": ["Documentation/networking/mac80211.rst"],
                    "code": ["net/wireless/", "drivers/net/wireless/"],
                },
            ]
        },
        {
            "category": "DEVICE DRIVERS",
            "domains": [
                {
                    "name": "gpu",
                    "title": "Graphics Processing Units",
                    "docs": ["Documentation/gpu/"],
                    "code": ["drivers/gpu/drm/"],
                },
                {
                    "name": "usb",
                    "title": "USB Subsystem",
                    "docs": ["Documentation/driver-api/usb/"],
                    "code": ["drivers/usb/", "include/linux/usb/"],
                },
                {
                    "name": "block",
                    "title": "Block Layer",
                    "docs": ["Documentation/block/"],
                    "code": ["block/", "drivers/block/"],
                },
            ]
        },
        {
            "category": "ARCHITECTURE-SPECIFIC",
            "domains": [
                {
                    "name": "x86",
                    "title": "x86 Architecture",
                    "docs": ["Documentation/arch/x86/", "Documentation/x86/"],
                    "code": ["arch/x86/"],
                },
                {
                    "name": "arm64",
                    "title": "ARM64 Architecture",
                    "docs": ["Documentation/arch/arm64/", "Documentation/arm64/"],
                    "code": ["arch/arm64/"],
                },
            ]
        },
    ]
    
    # Helper to calculate lines for a path pattern
    def get_lines_for_pattern(pattern: str) -> int:
        total = 0
        for dir_path, dir_data in dir_hierarchy.items():
            # Simple pattern matching
            if pattern.endswith('/'):
                if dir_path.startswith(pattern.rstrip('/')):
                    total += dir_data.get('total_lines', 0)
            elif '*' in pattern:
                base = pattern.split('*')[0]
                if dir_path.startswith(base):
                    total += dir_data.get('total_lines', 0)
            elif dir_path == pattern or dir_path.startswith(pattern + '\\'):
                total += dir_data.get('total_lines', 0)
        return total
    
    # Format each category
    for mapping in doc_mappings:
        lines.append(mapping["category"])
        lines.append("─" * 80)
        
        for domain in mapping["domains"]:
            lines.append(f"[{domain['name']}] {domain['title']}")
            lines.append(f"  Docs: {', '.join(domain['docs'])}")
            lines.append(f"  Code: {', '.join(domain['code'])}")
            
            # Calculate approximate LOC
            total_loc = sum(get_lines_for_pattern(path) for path in domain['code'])
            if total_loc > 0:
                lines.append(f"  Lines: ~{format_lines(total_loc)} LOC")
            
            lines.append("")
        
        lines.append("")
    
    lines.append("=" * 80)
    
    return "\n".join(lines)


def save_index_to_file(
    index_data: dict,
    output_path: str
) -> dict:
    """
    Save repository index to a plain text file.
    
    Args:
        index_data: Dictionary with repository index data (from scan_and_analyze_repository)
        output_path: Path to output file
        
    Returns:
        Dictionary with status and path information
    """
    try:
        output_file = Path(output_path)
        
        # Create parent directories if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Format the output
        content = format_index_to_text(index_data)
        
        # Write to file
        output_file.write_text(content, encoding='utf-8')
        
        return {
            "status": "success",
            "message": f"Index saved successfully to {output_path}",
            "path": str(output_file.absolute()),
            "size_bytes": len(content)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save index: {str(e)}",
            "path": None,
            "size_bytes": 0
        }
