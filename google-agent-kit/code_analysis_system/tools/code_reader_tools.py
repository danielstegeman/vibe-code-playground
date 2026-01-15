"""Tools for reading and analyzing source code files."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _get_repo_base_path() -> Path:
    """Get the base path of the Linux repository."""
    return Path(__file__).parent.parent.parent / 'linux_repo'


def read_source_file(
    file_path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    max_lines: int = 1000
) -> Dict[str, any]:
    """
    Read a source file from the repository.
    
    Args:
        file_path: Relative path to the file from repository root
        start_line: Optional starting line number (1-indexed)
        end_line: Optional ending line number (1-indexed, inclusive)
        max_lines: Maximum number of lines to return (default: 1000)
    
    Returns:
        Dictionary containing:
            - success: Whether the read was successful
            - content: File content (if successful)
            - lines_read: Number of lines read
            - total_lines: Total lines in file
            - file_path: The file path requested
            - error: Error message (if failed)
    """
    repo_path = _get_repo_base_path()
    full_path = repo_path / file_path
    
    if not full_path.exists():
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "file_path": file_path
        }
    
    if not full_path.is_file():
        return {
            "success": False,
            "error": f"Path is not a file: {file_path}",
            "file_path": file_path
        }
    
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        
        # Determine line range
        if start_line is None:
            start_line = 1
        if end_line is None:
            end_line = min(start_line + max_lines - 1, total_lines)
        
        # Validate line numbers
        start_line = max(1, min(start_line, total_lines))
        end_line = max(start_line, min(end_line, total_lines))
        
        # Enforce max_lines limit
        if end_line - start_line + 1 > max_lines:
            end_line = start_line + max_lines - 1
        
        # Extract requested lines (convert to 0-indexed)
        selected_lines = lines[start_line - 1:end_line]
        content = ''.join(selected_lines)
        
        return {
            "success": True,
            "content": content,
            "lines_read": len(selected_lines),
            "total_lines": total_lines,
            "file_path": file_path,
            "start_line": start_line,
            "end_line": end_line
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading file: {str(e)}",
            "file_path": file_path
        }


def search_in_directory(
    directory: str,
    pattern: str,
    file_extensions: Optional[List[str]] = None,
    max_results: int = 50
) -> Dict[str, any]:
    """
    Search for files matching a pattern in a directory.
    
    Args:
        directory: Relative directory path from repository root
        pattern: Search pattern (case-insensitive substring match in filenames)
        file_extensions: Optional list of extensions to filter (e.g., ['.c', '.h'])
        max_results: Maximum number of results to return
    
    Returns:
        Dictionary containing:
            - success: Whether the search was successful
            - matches: List of matching file paths
            - total_matches: Total number of matches found
            - directory: The directory searched
    """
    repo_path = _get_repo_base_path()
    search_path = repo_path / directory
    
    if not search_path.exists():
        return {
            "success": False,
            "error": f"Directory not found: {directory}",
            "directory": directory
        }
    
    if not search_path.is_dir():
        return {
            "success": False,
            "error": f"Path is not a directory: {directory}",
            "directory": directory
        }
    
    try:
        matches = []
        pattern_lower = pattern.lower()
        
        # Walk through directory
        for root, dirs, files in os.walk(search_path):
            # Skip common excluded directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
            
            for filename in files:
                # Check file extension filter
                if file_extensions:
                    if not any(filename.endswith(ext) for ext in file_extensions):
                        continue
                
                # Check pattern match
                if pattern_lower in filename.lower():
                    rel_path = os.path.relpath(os.path.join(root, filename), repo_path)
                    matches.append(rel_path.replace('\\', '/'))
                    
                    if len(matches) >= max_results:
                        break
            
            if len(matches) >= max_results:
                break
        
        return {
            "success": True,
            "matches": matches[:max_results],
            "total_matches": len(matches),
            "directory": directory,
            "pattern": pattern
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error searching directory: {str(e)}",
            "directory": directory
        }


def get_directory_summary(directory: str, max_depth: int = 2) -> Dict[str, any]:
    """
    Get a summary of a directory's contents.
    
    Args:
        directory: Relative directory path from repository root
        max_depth: Maximum depth to traverse (default: 2)
    
    Returns:
        Dictionary containing:
            - success: Whether the operation was successful
            - directory: The directory path
            - subdirectories: List of subdirectory names
            - file_count: Total number of files
            - file_types: Dictionary of file extensions and counts
            - sample_files: Sample of file names
    """
    repo_path = _get_repo_base_path()
    dir_path = repo_path / directory
    
    if not dir_path.exists():
        return {
            "success": False,
            "error": f"Directory not found: {directory}",
            "directory": directory
        }
    
    if not dir_path.is_dir():
        return {
            "success": False,
            "error": f"Path is not a directory: {directory}",
            "directory": directory
        }
    
    try:
        subdirectories = []
        file_types = {}
        sample_files = []
        file_count = 0
        
        # Get immediate subdirectories
        for item in dir_path.iterdir():
            if item.is_dir() and item.name not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}:
                subdirectories.append(item.name)
        
        # Count files and types up to max_depth
        for root, dirs, files in os.walk(dir_path):
            # Calculate current depth
            current_depth = root.replace(str(dir_path), '').count(os.sep)
            if current_depth >= max_depth:
                dirs[:] = []  # Don't descend further
                continue
            
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
            
            for filename in files:
                file_count += 1
                ext = os.path.splitext(filename)[1] or 'no_extension'
                file_types[ext] = file_types.get(ext, 0) + 1
                
                # Collect sample files
                if len(sample_files) < 20:
                    rel_path = os.path.relpath(os.path.join(root, filename), repo_path)
                    sample_files.append(rel_path.replace('\\', '/'))
        
        return {
            "success": True,
            "directory": directory,
            "subdirectories": sorted(subdirectories),
            "file_count": file_count,
            "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)),
            "sample_files": sample_files
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error analyzing directory: {str(e)}",
            "directory": directory
        }


def list_files_in_directory(
    directory: str,
    file_extensions: Optional[List[str]] = None,
    max_files: int = 100
) -> Dict[str, any]:
    """
    List all files in a directory (non-recursive).
    
    Args:
        directory: Relative directory path from repository root
        file_extensions: Optional list of extensions to filter
        max_files: Maximum number of files to return
    
    Returns:
        Dictionary containing:
            - success: Whether the operation was successful
            - files: List of file names
            - total_files: Total number of files found
            - directory: The directory path
    """
    repo_path = _get_repo_base_path()
    dir_path = repo_path / directory
    
    if not dir_path.exists():
        return {
            "success": False,
            "error": f"Directory not found: {directory}",
            "directory": directory
        }
    
    if not dir_path.is_dir():
        return {
            "success": False,
            "error": f"Path is not a directory: {directory}",
            "directory": directory
        }
    
    try:
        files = []
        
        for item in dir_path.iterdir():
            if item.is_file():
                if file_extensions:
                    if not any(item.name.endswith(ext) for ext in file_extensions):
                        continue
                
                files.append(item.name)
                
                if len(files) >= max_files:
                    break
        
        return {
            "success": True,
            "files": sorted(files),
            "total_files": len(files),
            "directory": directory
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error listing files: {str(e)}",
            "directory": directory
        }
