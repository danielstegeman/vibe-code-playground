import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count


def count_lines_in_file(file_path: Path) -> int:
    """Count total lines in a file. Returns 0 for binary/unreadable files."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        # Binary files or files we can't read - return 0
        return 0


def process_file_batch(file_paths: List[Tuple[Path, Path]]) -> List[Dict]:
    """
    Process a batch of files and count their lines.
    
    Args:
        file_paths: List of tuples (absolute_path, relative_path)
        
    Returns:
        List of dicts with file info and line counts
    """
    results = []
    for abs_path, rel_path in file_paths:
        try:
            extension = abs_path.suffix.lower() or "(no extension)"
            lines = count_lines_in_file(abs_path)
            
            results.append({
                "path": str(rel_path),
                "lines": lines,
                "extension": extension
            })
        except (PermissionError, OSError):
            # Skip files we can't access
            continue
    
    return results


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
    max_depth: int = -1,
    parallel: bool = True,
    max_workers: int = None
) -> dict:
    """
    Scan directory structure and analyze repository. Returns dict with analysis results.
    
    Args:
        root_path: Root directory to scan
        repo_url: Repository URL (optional, for metadata)
        repo_name: Repository name (optional, for metadata)
        max_depth: Maximum depth to scan (-1 for unlimited)
        parallel: Enable parallel processing (default: True)
        max_workers: Number of parallel workers (default: CPU count)
        
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
    
    # Set up parallel processing
    if max_workers is None:
        max_workers = cpu_count()
    
    print(f"        Using {max_workers} workers for parallel processing" if parallel else "        Using sequential processing")
    
    files_data = []
    dir_stats_data = {}
    max_depth_found = 0
    file_type_dist = defaultdict(int)
    total_lines = 0
    
    # Progress tracking
    files_processed = 0
    dirs_processed = 0
    progress_interval = 1000  # Log every 1000 files
    
    # Collect all file paths first for parallel processing
    file_paths_to_process = []
    # Progress tracking
    files_processed = 0
    dirs_processed = 0
    progress_interval = 1000  # Log every 1000 files
    
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
        
        # Progress logging for directories
        dirs_processed += 1
        if dirs_processed % 500 == 0:
            rel_display = str(current_dir.relative_to(root)) if current_dir != root else "."
            print(f"        ... processing: {rel_display} ({dirs_processed:,} dirs, {files_processed:,} files)")
        
        # Check depth limit
        depth = get_depth(current_dir)
        max_depth_found = max(max_depth_found, depth)
        
        if max_depth != -1 and depth >= max_depth:
            dirnames.clear()
            continue
        
        # Filter out excluded subdirectories
        dirnames[:] = [d for d in dirnames if not any(p in d for p in exclude_patterns)]
        
        # Initialize directory stats - use forward slashes for consistency
        rel_path = str(current_dir.relative_to(root)).replace('\\', '/') if current_dir != root else "."
        
        # Collect file paths for this directory
        for filename in filenames:
            file_path = current_dir / filename
            rel_file_path = file_path.relative_to(root)
            file_paths_to_process.append((file_path, rel_file_path))
        
        # Store directory structure (will populate stats after processing)
        dir_stats_data[rel_path] = {
            "path": rel_path,
            "total_files": len(filenames),
            "total_lines": 0,
            "subdirectories": dirnames.copy(),
            "file_types": defaultdict(int)
        }
    
    # Process files in parallel or sequential
    print(f"        ... counting lines in {len(file_paths_to_process):,} files")
    
    if parallel and len(file_paths_to_process) > 100:  # Only use parallel for substantial workloads
        # Split files into batches
        batch_size = max(1, len(file_paths_to_process) // (max_workers * 4))
        batches = [file_paths_to_process[i:i + batch_size] for i in range(0, len(file_paths_to_process), batch_size)]
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_batch = {executor.submit(process_file_batch, batch): batch for batch in batches}
            
            for future in as_completed(future_to_batch):
                batch_results = future.result()
                files_data.extend(batch_results)
                
                # Update progress
                files_processed += len(batch_results)
                if files_processed % progress_interval == 0 or files_processed == len(file_paths_to_process):
                    print(f"        ... {files_processed:,}/{len(file_paths_to_process):,} files processed")
    else:
        # Sequential processing for small workloads
        batch_results = process_file_batch(file_paths_to_process)
        files_data.extend(batch_results)
        print(f"        ... {len(files_data):,} files processed")
    
    # Update directory statistics and totals with file data
    print(f"        ... updating directory statistics")
    for file_info in files_data:
        extension = file_info["extension"]
        lines = file_info["lines"]
        
        total_lines += lines
        file_type_dist[extension] += 1
        
        # Find parent directory
        file_path_str = str(file_info["path"]).replace('\\', '/')
        dir_path = "/".join(Path(file_path_str).parts[:-1]) if "/" in file_path_str or "\\" in str(file_info["path"]) else "."
        
        if dir_path in dir_stats_data:
            dir_stats_data[dir_path]["total_lines"] += lines
            dir_stats_data[dir_path]["file_types"][extension] += 1
    
    # Convert defaultdicts to regular dicts
    for dir_data in dir_stats_data.values():
        dir_data["file_types"] = dict(dir_data["file_types"])
    
    print(f"        ... aggregating directory statistics ({len(dir_stats_data):,} directories)")
    
    # Find files with most lines (top 50)
    files_by_lines = sorted(files_data, key=lambda f: f["lines"], reverse=True)[:50]
    
    # Aggregate lines for parent directories - process from deepest to shallowest
    sorted_dirs = sorted(dir_stats_data.keys(), key=lambda p: p.count('/'), reverse=True)
    for dir_path in sorted_dirs:
        dir_data = dir_stats_data[dir_path]
        # Add subdirectory lines to this directory's count
        for subdir in dir_data["subdirectories"]:
            subdir_path = f"{dir_path}/{subdir}" if dir_path != "." else subdir
            if subdir_path in dir_stats_data:
                dir_data["total_lines"] += dir_stats_data[subdir_path]["total_lines"]
    
    return {
        "status": "success",
        "repository_url": repo_url,
        "repository_name": repo_name,
        "indexed_at": datetime.now().isoformat(),
        "total_files": len(files_data),
        "total_directories": len(dir_stats_data),
        "total_lines": total_lines,
        "max_depth": max_depth_found,
        "file_type_distribution": dict(file_type_dist),
        "directory_hierarchy": dir_stats_data,
        "files_by_lines": files_by_lines
    }
