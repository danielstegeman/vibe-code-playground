from pathlib import Path
from typing import Dict, List


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"


def format_index_to_text(index_data: dict) -> str:
    """
    Format repository index data to human-readable plain text.
    
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
    lines.append(f"Total Size: {format_bytes(index_data.get('total_size_bytes', 0))}")
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
        for ext, count in sorted_types[:20]:  # Top 20 file types
            percentage = (count / total_files * 100) if total_files > 0 else 0
            ext_display = ext if ext else "(no extension)"
            lines.append(f"{ext_display:20} {count:8,} files ({percentage:5.2f}%)")
        lines.append("")
    
    # Largest files
    largest_files = index_data.get('largest_files', [])
    if largest_files:
        lines.append("-" * 80)
        lines.append("LARGEST FILES")
        lines.append("-" * 80)
        for i, file_info in enumerate(largest_files[:10], 1):  # Top 10 largest
            lines.append(f"{i:2}. {format_bytes(file_info['size_bytes']):>10} - {file_info['path']}")
        lines.append("")
    
    # Directory statistics
    dir_stats = index_data.get('directory_stats', [])
    if dir_stats:
        lines.append("-" * 80)
        lines.append("DIRECTORY STATISTICS (Top 20 by file count)")
        lines.append("-" * 80)
        sorted_dirs = sorted(dir_stats, key=lambda x: x['total_files'], reverse=True)
        for dir_stat in sorted_dirs[:20]:
            lines.append(f"\n{dir_stat['path']}")
            lines.append(f"  Files: {dir_stat['total_files']:,} | Subdirs: {dir_stat['subdirectories']:,} | Size: {format_bytes(dir_stat['total_size_bytes'])}")
            if dir_stat.get('file_types'):
                top_types = sorted(dir_stat['file_types'].items(), key=lambda x: x[1], reverse=True)[:5]
                type_str = ", ".join([f"{ext}({count})" for ext, count in top_types])
                lines.append(f"  Top types: {type_str}")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF REPORT")
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
