"""Tools for reading and querying repository indexes."""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional


def read_index_file(index_type: str, repo_name: str = "linux") -> str:
    """
    Read a specific index file for a repository.
    
    Args:
        index_type: Type of index to read. Options:
            - 'hierarchy': Hierarchical tree structure
            - 'summary': Summary statistics
            - 'documentation': Documentation subdomain guide
        repo_name: Name of the repository (default: 'linux')
    
    Returns:
        Content of the index file as a string
    """
    # Map index types to file patterns
    index_files = {
        'hierarchy': f'{repo_name}_hierarchical_index.txt',
        'summary': f'{repo_name}_summary.txt',
        'documentation': f'{repo_name}_documentation_guide.txt',
    }
    
    if index_type not in index_files:
        return f"Error: Unknown index type '{index_type}'. Valid types: {list(index_files.keys())}"
    
    # Get the outputs/indexes directory
    base_dir = Path(__file__).parent.parent.parent / 'outputs' / 'indexes'
    index_path = base_dir / index_files[index_type]
    
    if not index_path.exists():
        return f"Error: Index file not found at {index_path}"
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading index file: {str(e)}"


def query_subdomain_info(subdomain_name: str, repo_name: str = "linux") -> Dict[str, any]:
    """
    Query information about a specific subdomain from the documentation guide.
    
    Args:
        subdomain_name: Name of the subdomain (e.g., 'kernel', 'mm', 'networking')
        repo_name: Name of the repository (default: 'linux')
    
    Returns:
        Dictionary containing:
            - subdomain: The subdomain name
            - title: Full title of the subdomain
            - docs: Documentation paths
            - code: Code paths
            - lines: Estimated lines of code
            - found: Whether the subdomain was found
    """
    content = read_index_file('documentation', repo_name)
    
    if content.startswith("Error:"):
        return {"found": False, "error": content}
    
    # Parse the documentation guide to find the subdomain
    pattern = rf'\[{re.escape(subdomain_name)}\]\s+(.+?)\n\s+Docs:\s+(.+?)\n\s+Code:\s+(.+?)\n\s+Lines:\s+(.+?)(?:\n|$)'
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        return {
            "found": False,
            "subdomain": subdomain_name,
            "error": f"Subdomain '{subdomain_name}' not found in documentation guide"
        }
    
    title, docs, code, lines = match.groups()
    
    return {
        "found": True,
        "subdomain": subdomain_name,
        "title": title.strip(),
        "docs": docs.strip(),
        "code": code.strip(),
        "lines": lines.strip(),
    }


def get_all_subdomains(repo_name: str = "linux") -> List[Dict[str, str]]:
    """
    Get a list of all available subdomains from the documentation guide.
    
    Args:
        repo_name: Name of the repository (default: 'linux')
    
    Returns:
        List of dictionaries, each containing:
            - subdomain: The subdomain identifier
            - title: Full title
            - category: Category (CORE SUBSYSTEMS, FILESYSTEMS, etc.)
    """
    content = read_index_file('documentation', repo_name)
    
    if content.startswith("Error:"):
        return []
    
    subdomains = []
    current_category = None
    
    # Parse the file to extract all subdomains
    lines = content.split('\n')
    for line in lines:
        # Check if this is a category header
        if line.isupper() and not line.startswith('=') and not line.startswith('─'):
            current_category = line.strip()
            continue
        
        # Check if this is a subdomain entry
        match = re.match(r'\[(\w+)\]\s+(.+)', line)
        if match:
            subdomain_id, title = match.groups()
            subdomains.append({
                "subdomain": subdomain_id,
                "title": title.strip(),
                "category": current_category or "Unknown"
            })
    
    return subdomains


def recommend_code_locations(query: str, repo_name: str = "linux") -> List[Dict[str, str]]:
    """
    Recommend code locations based on a natural language query.
    
    Args:
        query: Natural language query about the codebase
        repo_name: Name of the repository (default: 'linux')
    
    Returns:
        List of relevant subdomain information dictionaries, ranked by relevance
    """
    # Get all subdomains
    all_subdomains = get_all_subdomains(repo_name)
    
    if not all_subdomains:
        return []
    
    # Simple keyword matching for relevance scoring
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))
    
    scored_subdomains = []
    for subdomain_info in all_subdomains:
        # Get full details for scoring
        full_info = query_subdomain_info(subdomain_info['subdomain'], repo_name)
        
        if not full_info.get('found'):
            continue
        
        # Score based on keyword matches
        score = 0
        search_text = (
            f"{subdomain_info['subdomain']} {subdomain_info['title']} "
            f"{full_info.get('docs', '')} {full_info.get('code', '')}"
        ).lower()
        
        for word in query_words:
            if word in search_text:
                score += 1
        
        if score > 0:
            full_info['relevance_score'] = score
            scored_subdomains.append(full_info)
    
    # Sort by relevance score (descending)
    scored_subdomains.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return scored_subdomains
