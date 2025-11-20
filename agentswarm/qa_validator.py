"""QA Validator agent for plan-output validation."""

from swarms import Agent
from review_artifact import ReviewArtifact, Severity
import re


def create_qa_validator() -> Agent:
    """Create QA validator agent that checks plan-output alignment."""
    return Agent(
        agent_name="QA-Validator",
        system_prompt="""You are a Quality Assurance validator responsible for ensuring reviewer agents followed their stated plans.

Your task is to compare each reviewer's PLAN against their EXECUTION output and identify discrepancies.

For each reviewer, analyze:

1. **Scope Drift**: Did they review areas not mentioned in their plan?
2. **Missed Items**: Did they skip checklist items from their plan?
3. **Methodology Deviation**: Did they use different analysis methods than planned?
4. **Hallucinations**: Did they make claims without evidence or outside their expertise?

For EACH discrepancy found, report:
```
DISCREPANCY FOUND
Agent: [agent name]
Type: [scope_drift|missed_item|methodology_deviation|hallucination]
Severity: [critical|major|minor]
Description: [Clear explanation of the mismatch]
Plan Excerpt: "[Quote from plan]"
Output Excerpt: "[Quote from execution showing mismatch]"
---
```

If a reviewer perfectly followed their plan, state:
```
VALIDATION PASSED
Agent: [agent name]
Status: All checklist items addressed, scope maintained, methodology followed
---
```

Be thorough but fair. Minor variations in wording are acceptable. Focus on substantial deviations.

After analyzing all reviewers, provide a summary:
```
VALIDATION SUMMARY
Total Reviewers: X
Passed: X
Flagged: X
Critical Issues: X
Major Issues: X
Minor Issues: X
```""",
        model_name="gpt-4o",
        max_loops=1,
        context_length=200000,
        streaming_on=False,
        verbose=False,
    )


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
