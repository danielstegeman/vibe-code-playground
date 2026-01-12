import os
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from collections import defaultdict


def clone_repository(repo_url: str, target_dir: str, shallow: bool = True) -> dict:
    """
    Clone a git repository to a target directory.
    
    Args:
        repo_url: URL of the git repository
        target_dir: Local directory to clone into
        shallow: If True, perform shallow clone (depth=1) for faster cloning
        
    Returns:
        Dictionary with status and path information
    """
    try:
        target_path = Path(target_dir)
        
        # Check if directory exists and is not empty
        if target_path.exists() and any(target_path.iterdir()):
            return {
                "status": "exists",
                "message": f"Repository already exists at {target_dir}",
                "path": str(target_path.absolute())
            }
        
        # Create target directory if it doesn't exist
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Build git clone command
        cmd = ["git", "clone"]
        if shallow:
            cmd.extend(["--depth", "1"])
        cmd.extend([repo_url, str(target_path)])
        
        # Execute clone
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Successfully cloned repository to {target_dir}",
                "path": str(target_path.absolute())
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to clone: {result.stderr}",
                "path": None
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Clone operation timed out after 10 minutes",
            "path": None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error cloning repository: {str(e)}",
            "path": None
        }


def scan_and_analyze_repository(
    root_path: str,
    repo_url: str = "",
    repo_name: str = "",
    max_depth: int = -1
) -> dict:
    """
    Scan directory structure and analyze repository. Returns dict with analysis results.
    
    Args:
        root_path: Root directory to scan
        repo_url: Repository URL (optional, for metadata)
        repo_name: Repository name (optional, for metadata)
        max_depth: Maximum depth to scan (-1 for unlimited)
        
    Returns:
        Dictionary with scan results and statistics
    """
    exclude_patterns = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
    
    root = Path(root_path)
    if not root.exists():
        return {
            "status": "error",
            "message": f"Path does not exist: {root_path}"
        }
    
    # Derive repo name from path if not provided
    if not repo_name:
        repo_name = root.name
    
    files_data = []
    dir_stats_data = []
    max_depth_found = 0
    file_type_dist = defaultdict(int)
    total_size = 0
    
    def should_exclude(path: Path) -> bool:
        """Check if path should be excluded."""
        for pattern in exclude_patterns:
            if pattern in path.parts:
                return True
        return False
    
    def get_depth(path: Path) -> int:
        """Calculate depth relative to root."""
        try:
            relative = path.relative_to(root)
            return len(relative.parts)
        except ValueError:
            return 0
    
    # Walk through directory tree
    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)
        
        # Check if we should exclude this directory
        if should_exclude(current_dir):
            dirnames.clear()
            continue
        
        # Check depth limit
        depth = get_depth(current_dir)
        max_depth_found = max(max_depth_found, depth)
        
        if max_depth != -1 and depth >= max_depth:
            dirnames.clear()
            continue
        
        # Filter out excluded subdirectories
        dirnames[:] = [d for d in dirnames if not any(p in d for p in exclude_patterns)]
        
        # Initialize directory stats
        rel_path = str(current_dir.relative_to(root)) if current_dir != root else "."
        dir_file_types = defaultdict(int)
        dir_total_files = 0
        dir_total_size = 0
        
        # Process files in current directory
        for filename in filenames:
            file_path = current_dir / filename
            
            try:
                # Get file stats
                stat_info = file_path.stat()
                extension = file_path.suffix.lower() or "(no extension)"
                
                # Store file info
                file_data = {
                    "path": str(file_path.relative_to(root)),
                    "size_bytes": stat_info.st_size,
                    "extension": extension
                }
                files_data.append(file_data)
                
                # Update stats
                dir_total_files += 1
                dir_total_size += stat_info.st_size
                dir_file_types[extension] += 1
                file_type_dist[extension] += 1
                total_size += stat_info.st_size
                
            except (PermissionError, OSError):
                # Skip files we can't access
                continue
        
        # Store directory stats
        dir_stats_data.append({
            "path": rel_path,
            "total_files": dir_total_files,
            "total_size_bytes": dir_total_size,
            "subdirectories": len(dirnames),
            "file_types": dict(dir_file_types)
        })
    
    # Find largest files (limit to top 50 to avoid huge responses)
    largest_files = sorted(files_data, key=lambda f: f["size_bytes"], reverse=True)[:50]
    
    # Limit directory stats to top 100 by file count
    top_dirs = sorted(dir_stats_data, key=lambda d: d["total_files"], reverse=True)[:100]
    
    return {
        "status": "success",
        "repository_url": repo_url,
        "repository_name": repo_name,
        "indexed_at": datetime.now().isoformat(),
        "total_files": len(files_data),
        "total_directories": len(dir_stats_data),
        "total_size_bytes": total_size,
        "max_depth": max_depth_found,
        "file_type_distribution": dict(file_type_dist),
        "directory_stats": top_dirs,  # Only top 100 directories
        "largest_files": largest_files,
        "note": "Directory stats and file lists are limited to reduce response size"
    }
