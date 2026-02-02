"""Tools for routing queries and managing agent communication."""

from typing import Dict, List, Optional
import re
from google.adk.agents.llm_agent import Agent


def create_subdomain_context(
    subdomain: str,
    code_paths: str,
    lines_of_code: str,
    max_lines_per_agent: int = 100000
) -> List[Dict[str, any]]:
    """
    Create context information for subdomain agents based on LOC limits.
    
    Args:
        subdomain: The subdomain identifier
        code_paths: Comma-separated code paths for this subdomain
        lines_of_code: LOC estimate (e.g., "~65,958 LOC")
        max_lines_per_agent: Maximum lines of code per subdomain agent
    
    Returns:
        List of subdomain contexts, potentially split if LOC exceeds limit.
        Each context contains:
            - subdomain: Original subdomain identifier
            - paths: List of paths to analyze
            - estimated_lines: Estimated LOC for this chunk
            - chunk_id: Identifier if split into multiple chunks
    """
    # Parse LOC from string (e.g., "~65,958 LOC" -> 65958)
    loc_match = re.search(r'[\d,]+', lines_of_code)
    if loc_match:
        estimated_loc = int(loc_match.group().replace(',', ''))
    else:
        estimated_loc = 0
    
    # Parse code paths
    paths = [p.strip() for p in code_paths.split(',')]
    
    # Check if we need to split
    if estimated_loc <= max_lines_per_agent or len(paths) == 1:
        # Single agent can handle this
        return [{
            "subdomain": subdomain,
            "paths": paths,
            "estimated_lines": estimated_loc,
            "chunk_id": 0,
            "total_chunks": 1
        }]
    
    # Need to split into multiple chunks
    # Simple strategy: divide paths evenly
    num_chunks = (estimated_loc // max_lines_per_agent) + 1
    chunk_size = len(paths) // num_chunks + (1 if len(paths) % num_chunks else 0)
    
    contexts = []
    for i in range(0, len(paths), chunk_size):
        chunk_paths = paths[i:i + chunk_size]
        chunk_id = i // chunk_size
        
        contexts.append({
            "subdomain": subdomain,
            "paths": chunk_paths,
            "estimated_lines": estimated_loc // num_chunks,
            "chunk_id": chunk_id,
            "total_chunks": num_chunks
        })
    
    return contexts


def aggregate_agent_responses(responses: List[Dict[str, any]]) -> Dict[str, any]:
    """
    Aggregate responses from multiple subdomain agents.
    
    Args:
        responses: List of response dictionaries from subdomain agents.
            Each should contain:
                - agent_id: Identifier for the agent
                - subdomain: Subdomain analyzed
                - findings: Text findings from the agent
                - file_references: List of files referenced
    
    Returns:
        Aggregated response dictionary containing:
            - total_agents: Number of agents that responded
            - subdomains: List of subdomains covered
            - combined_findings: All findings combined
            - all_file_references: All unique file references
    """
    if not responses:
        return {
            "total_agents": 0,
            "subdomains": [],
            "combined_findings": "",
            "all_file_references": []
        }
    
    subdomains = set()
    all_findings = []
    all_files = set()
    
    for response in responses:
        if 'subdomain' in response:
            subdomains.add(response['subdomain'])
        
        if 'findings' in response:
            agent_label = response.get('agent_id', 'Unknown Agent')
            all_findings.append(f"=== {agent_label} ===\n{response['findings']}\n")
        
        if 'file_references' in response:
            all_files.update(response['file_references'])
    
    return {
        "total_agents": len(responses),
        "subdomains": sorted(list(subdomains)),
        "combined_findings": "\n".join(all_findings),
        "all_file_references": sorted(list(all_files))
    }


def format_agent_handoff(
    from_agent: str,
    to_agent: str,
    context: Dict[str, any],
    instruction: str
) -> str:
    """
    Format a handoff message between agents.
    
    Args:
        from_agent: Name of the sending agent
        to_agent: Name of the receiving agent
        context: Context dictionary to pass
        instruction: Specific instruction for the receiving agent
    
    Returns:
        Formatted handoff message
    """
    message = f"""
AGENT HANDOFF
=============
From: {from_agent}
To: {to_agent}

Instruction:
{instruction}

Context:
"""
    
    for key, value in context.items():
        if isinstance(value, (list, dict)):
            message += f"\n{key}:\n  {value}\n"
        else:
            message += f"\n{key}: {value}\n"
    
    return message


def spawn_subdomain_agent(
    subdomain: str,
    code_paths: str,
    task_description: str,
    focus_question: str,
    agent_id: Optional[str] = None
) -> Dict[str, any]:
    """
    Spawn a new subdomain agent to analyze specific code paths.
    
    This tool allows the mediator to create additional subdomain agents
    when gaps are identified in the analysis or follow-up investigation
    is needed.
    
    Args:
        subdomain: The subdomain this agent will analyze (e.g., "scheduler", "memory_management")
        code_paths: Comma-separated list of paths to examine (e.g., "kernel/sched/, kernel/time/")
        task_description: What this agent should accomplish
        focus_question: Specific question for the agent to answer
        agent_id: Optional custom identifier for the agent (auto-generated if not provided)
    
    Returns:
        Dictionary containing:
            - agent_id: The identifier of the spawned agent
            - subdomain: The subdomain being analyzed
            - paths: List of code paths assigned
            - status: "completed" or "error"
            - result: Analysis result from the agent (populated after execution)
            - error: Error message if status is "error"
    
    Example:
        spawn_subdomain_agent(
            subdomain="scheduler",
            code_paths="kernel/sched/core.c, kernel/sched/fair.c",
            task_description="Analyze scheduler preemption logic",
            focus_question="How does the scheduler decide when to preempt a running task?",
            agent_id="scheduler_preemption_agent"
        )
    """
    from ..agents.subdomain import create_subdomain_agent
    
    # Parse paths
    paths = [p.strip() for p in code_paths.split(',')]
    
    # Generate agent ID if not provided
    if agent_id is None:
        subdomain_clean = subdomain.replace(' ', '_').lower()
        agent_id = f"subdomain_agent_{subdomain_clean}"
    
    try:
        # Create the agent - ADK agents must be invoked through the runner, not .run()
        # The spawn tool cannot directly execute agents synchronously
        # Instead, return the agent configuration for the mediator to handle
        
        return {
            "agent_id": agent_id,
            "subdomain": subdomain,
            "paths": paths,
            "status": "error",
            "error": "spawn_subdomain_agent cannot be used as a tool. The mediator should create subdomain agents by transferring to them via ADK's sub_agents mechanism, not by calling this tool."
        }
        
    except Exception as e:
        return {
            "agent_id": agent_id,
            "subdomain": subdomain,
            "paths": paths,
            "status": "error",
            "error": str(e)
        }
