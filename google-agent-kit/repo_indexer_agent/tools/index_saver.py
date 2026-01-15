from pathlib import Path
from .output_formatter import (
    format_hierarchy_tree,
    format_index_to_text,
    create_documentation_index
)


def save_all_indexes(
    index_data: dict,
    output_dir: str,
    repo_name: str = None
) -> dict:
    """
    Save all index formats: hierarchy tree, summary stats, and documentation subdomain guide.
    
    Args:
        index_data: Dictionary with repository index data (from scan_and_analyze_repository)
        output_dir: Directory to save index files
        repo_name: Optional repository name for filenames (defaults to repository_name from index_data)
        
    Returns:
        Dictionary with status and paths of saved files
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if not repo_name:
            repo_name = index_data.get('repository_name', 'repository')
        
        results = {}
        
        # 1. Save hierarchical tree index (primary, token-optimized)
        hierarchy_file = output_path / f"{repo_name}_hierarchy.txt"
        hierarchy_content = format_hierarchy_tree(index_data)
        hierarchy_file.write_text(hierarchy_content, encoding='utf-8')
        results['hierarchy'] = {
            'path': str(hierarchy_file.absolute()),
            'size': len(hierarchy_content)
        }
        
        # 2. Save summary statistics index
        summary_file = output_path / f"{repo_name}_summary.txt"
        summary_content = format_index_to_text(index_data)
        summary_file.write_text(summary_content, encoding='utf-8')
        results['summary'] = {
            'path': str(summary_file.absolute()),
            'size': len(summary_content)
        }
        
        # 3. Save documentation subdomain navigation index
        docs_file = output_path / f"{repo_name}_documentation_guide.txt"
        docs_content = create_documentation_index(index_data)
        docs_file.write_text(docs_content, encoding='utf-8')
        results['documentation'] = {
            'path': str(docs_file.absolute()),
            'size': len(docs_content)
        }
        
        return {
            "status": "success",
            "message": f"All indexes saved successfully to {output_dir}",
            "files": results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save indexes: {str(e)}",
            "files": {}
        }
