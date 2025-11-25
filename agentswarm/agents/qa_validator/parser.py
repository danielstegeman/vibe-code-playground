"""Parser for QA validator output."""

from core.models import ReviewArtifact, Severity
import re


def parse_qa_validation(qa_output: str, artifacts: list[ReviewArtifact]) -> list[ReviewArtifact]:
    """
    Parse QA validator output and update review artifacts with discrepancies.
    
    Args:
        qa_output: The output from QA validator agent
        artifacts: List of ReviewArtifact objects to update
        
    Returns:
        Updated list of ReviewArtifact objects
    """
    # Create a map of agent names to artifacts for quick lookup
    artifact_map = {artifact.agent_name: artifact for artifact in artifacts}
    
    # Parse discrepancies using regex
    discrepancy_pattern = r'DISCREPANCY FOUND\s+Agent:\s*(.+?)\s+Type:\s*(\w+)\s+Severity:\s*(\w+)\s+Description:\s*(.+?)\s+Plan Excerpt:\s*"(.+?)"\s+Output Excerpt:\s*"(.+?)"'
    
    matches = re.finditer(discrepancy_pattern, qa_output, re.DOTALL)
    
    for match in matches:
        agent_name = match.group(1).strip()
        disc_type = match.group(2).strip()
        severity_str = match.group(3).strip().lower()
        description = match.group(4).strip()
        plan_excerpt = match.group(5).strip()
        output_excerpt = match.group(6).strip()
        
        # Map severity string to enum
        severity_map = {
            'critical': Severity.CRITICAL,
            'major': Severity.MAJOR,
            'minor': Severity.MINOR
        }
        severity = severity_map.get(severity_str, Severity.MINOR)
        
        # Find matching artifact and add discrepancy
        if agent_name in artifact_map:
            artifact_map[agent_name].add_discrepancy(
                type=disc_type,
                severity=severity,
                description=description,
                plan_excerpt=plan_excerpt,
                output_excerpt=output_excerpt
            )
    
    # Parse passed validations
    passed_pattern = r'VALIDATION PASSED\s+Agent:\s*(.+?)\s+Status:'
    passed_matches = re.finditer(passed_pattern, qa_output, re.DOTALL)
    
    for match in passed_matches:
        agent_name = match.group(1).strip()
        if agent_name in artifact_map:
            artifact_map[agent_name].validation_status = "validated"
    
    return artifacts
