"""Orchestrator for the multi-agent code analysis system."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from .agents import director_agent, librarian_agent, create_subdomain_agent, mediator_agent


@dataclass
class AnalysisContext:
    """Context for a code analysis session."""
    query: str
    relevant_subdomains: List[Dict]
    subdomain_agents: List
    findings: List[Dict]
    final_response: Optional[str] = None


class CodeAnalysisOrchestrator:
    """Orchestrates the multi-agent code analysis workflow."""
    
    def __init__(self, max_lines_per_agent: int = 100000):
        """
        Initialize the orchestrator.
        
        Args:
            max_lines_per_agent: Maximum lines of code per subdomain agent
        """
        self.max_lines_per_agent = max_lines_per_agent
        self.director = director_agent
        self.librarian = librarian_agent
        self.mediator = mediator_agent
    
    def analyze(self, query: str) -> str:
        """
        Analyze a query about the Linux codebase.
        
        Args:
            query: User's question about the codebase
        
        Returns:
            Synthesized answer from the analysis
        """
        print(f"\n{'='*80}")
        print(f"STARTING ANALYSIS")
        print(f"{'='*80}")
        print(f"Query: {query}\n")
        
        # Phase 1: Director formulates plan
        print("[Phase 1] Director: Formulating analysis plan...")
        director_plan = self.director.run(
            f"User query: {query}\n\n"
            f"Create a plan for answering this question. Consider:\n"
            f"1. What aspects of the Linux kernel does this query touch?\n"
            f"2. What information needs to be extracted?\n"
            f"3. How should the analysis be structured?"
        )
        print(f"Director's plan:\n{director_plan}\n")
        
        # Phase 2: Librarian identifies relevant code locations
        print("[Phase 2] Librarian: Identifying relevant code locations...")
        librarian_response = self.librarian.run(
            f"User query: {query}\n\n"
            f"Director's plan: {director_plan}\n\n"
            f"Based on the repository indexes, recommend:\n"
            f"1. Which subdomains are most relevant\n"
            f"2. What code paths should be examined\n"
            f"3. Estimated complexity (LOC) for each area"
        )
        print(f"Librarian's recommendations:\n{librarian_response}\n")
        
        # Phase 3: Director decides on subdomain agent allocation
        print("[Phase 3] Director: Allocating subdomain agents...")
        allocation_decision = self.director.run(
            f"Librarian's recommendations:\n{librarian_response}\n\n"
            f"Maximum lines per agent: {self.max_lines_per_agent}\n\n"
            f"Decide:\n"
            f"1. Which subdomains to analyze\n"
            f"2. How many agents are needed\n"
            f"3. What each agent should focus on\n\n"
            f"Format your response as a clear list of agent assignments."
        )
        print(f"Agent allocation:\n{allocation_decision}\n")
        
        # Phase 4: Create and run subdomain agents
        # Note: In a full implementation, this would parse the allocation decision
        # and dynamically create agents. For now, we'll create a single agent
        # as a proof of concept
        print("[Phase 4] Subdomain Agent(s): Analyzing code...")
        
        # TODO: Parse allocation_decision to extract subdomain and paths
        # For now, using a simple approach
        subdomain_agent = create_subdomain_agent(
            subdomain="kernel",
            paths=["kernel/sched/", "include/linux/sched/"],
            agent_id="subdomain_agent_1"
        )
        
        subdomain_findings = subdomain_agent.run(
            f"User query: {query}\n\n"
            f"Director's instructions: Analyze the code in your assigned paths to help answer this query.\n\n"
            f"Provide:\n"
            f"1. Relevant code structures and patterns\n"
            f"2. Key files and their purposes\n"
            f"3. Specific examples from the code\n"
            f"4. How the code addresses the query"
        )
        print(f"Subdomain findings:\n{subdomain_findings}\n")
        
        # Phase 5: Mediator synthesizes final answer
        print("[Phase 5] Mediator: Synthesizing final answer...")
        final_answer = self.mediator.run(
            f"User query: {query}\n\n"
            f"Director's plan:\n{director_plan}\n\n"
            f"Librarian's recommendations:\n{librarian_response}\n\n"
            f"Subdomain Agent findings:\n{subdomain_findings}\n\n"
            f"Synthesize a comprehensive answer that:\n"
            f"1. Directly answers the user's question\n"
            f"2. Provides supporting evidence from code\n"
            f"3. Includes specific file references\n"
            f"4. Explains how things work\n"
            f"5. Notes any limitations or caveats"
        )
        
        print(f"\n{'='*80}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
        
        return final_answer
    
    def analyze_interactive(self, query: str) -> AnalysisContext:
        """
        Perform an interactive analysis where each phase can be inspected.
        
        Args:
            query: User's question about the codebase
        
        Returns:
            AnalysisContext with all intermediate results
        """
        context = AnalysisContext(
            query=query,
            relevant_subdomains=[],
            subdomain_agents=[],
            findings=[]
        )
        
        # Store phases for inspection
        return context


def run_analysis(query: str, max_lines_per_agent: int = 100000) -> str:
    """
    Convenience function to run a complete analysis.
    
    Args:
        query: User's question about the Linux codebase
        max_lines_per_agent: Maximum lines of code per subdomain agent
    
    Returns:
        Final synthesized answer
    """
    orchestrator = CodeAnalysisOrchestrator(max_lines_per_agent=max_lines_per_agent)
    return orchestrator.analyze(query)
