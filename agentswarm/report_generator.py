"""Markdown report generator for PR reviews."""

from datetime import datetime
from review_artifact import ReviewArtifact, Severity
from pathlib import Path


def generate_markdown_report(
    pr_number: str,
    pr_description: str,
    artifacts: list[ReviewArtifact],
    qa_output: str,
    director_output: str,
    output_dir: str = "reviews"
) -> str:
    """
    Generate a comprehensive markdown review report.
    
    Args:
        pr_number: Pull request number or identifier
        pr_description: Description of the PR being reviewed
        artifacts: List of ReviewArtifact objects from all reviewers
        qa_output: Raw output from QA validator
        director_output: Final synthesis from director
        output_dir: Directory to save the report
        
    Returns:
        Path to the generated markdown file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pr_review_{pr_number}_{timestamp}.md"
    filepath = Path(output_dir) / filename
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Build markdown content
    content = _build_report_content(pr_number, pr_description, artifacts, qa_output, director_output, timestamp)
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(filepath)


def _build_report_content(
    pr_number: str,
    pr_description: str,
    artifacts: list[ReviewArtifact],
    qa_output: str,
    director_output: str,
    timestamp: str
) -> str:
    """Build the complete markdown report content."""
    
    lines = []
    
    # Header
    lines.append(f"# Pull Request Review Report")
    lines.append(f"\n**PR Number:** {pr_number}")
    lines.append(f"**Review Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Review ID:** {timestamp}")
    lines.append(f"\n---\n")
    
    # PR Description
    lines.append(f"## Pull Request Description\n")
    lines.append(f"{pr_description}\n")
    lines.append(f"\n---\n")
    
    # Table of Contents
    lines.append(f"## Table of Contents\n")
    lines.append(f"1. [Executive Summary](#executive-summary)")
    lines.append(f"2. [QA Validation Findings](#qa-validation-findings)")
    lines.append(f"3. [Detailed Agent Reviews](#detailed-agent-reviews)")
    for artifact in artifacts:
        agent_anchor = artifact.agent_name.lower().replace(' ', '-').replace('_', '-')
        lines.append(f"   - [{artifact.agent_name}](#{agent_anchor})")
    lines.append(f"4. [Human Review Required](#human-review-required)")
    lines.append(f"\n---\n")
    
    # Executive Summary (Director's output)
    lines.append(f"## Executive Summary\n")
    lines.append(f"{director_output}\n")
    lines.append(f"\n---\n")
    
    # QA Validation Findings
    lines.append(f"## QA Validation Findings\n")
    lines.append(f"### Validation Summary\n")
    
    total_reviewers = len(artifacts)
    passed = sum(1 for a in artifacts if not a.has_issues())
    flagged = sum(1 for a in artifacts if a.has_issues())
    critical = sum(1 for a in artifacts for d in a.discrepancies if d.severity == Severity.CRITICAL)
    major = sum(1 for a in artifacts for d in a.discrepancies if d.severity == Severity.MAJOR)
    minor = sum(1 for a in artifacts for d in a.discrepancies if d.severity == Severity.MINOR)
    
    lines.append(f"- **Total Reviewers:** {total_reviewers}")
    lines.append(f"- **Validation Passed:** {passed} ✅")
    lines.append(f"- **Validation Flagged:** {flagged} ⚠️")
    lines.append(f"- **Critical Issues:** {critical} 🔴")
    lines.append(f"- **Major Issues:** {major} 🟡")
    lines.append(f"- **Minor Issues:** {minor} ⚪")
    lines.append(f"\n### Discrepancy Details\n")
    
    if flagged == 0:
        lines.append(f"✅ All reviewers followed their plans perfectly. No discrepancies detected.\n")
    else:
        for artifact in artifacts:
            if not artifact.has_issues():
                continue
            
            lines.append(f"#### {artifact.agent_name}\n")
            lines.append(f"**Status:** {artifact.validation_status.upper()}")
            lines.append(f"\n")
            
            for i, disc in enumerate(artifact.discrepancies, 1):
                severity_badge = _get_severity_badge(disc.severity)
                lines.append(f"**Discrepancy {i}:** {severity_badge}\n")
                lines.append(f"- **Type:** {disc.type}")
                lines.append(f"- **Severity:** {disc.severity.value.upper()}")
                lines.append(f"- **Description:** {disc.description}")
                lines.append(f"- **Plan Excerpt:**")
                lines.append(f"  > {disc.plan_excerpt}")
                lines.append(f"- **Output Excerpt:**")
                lines.append(f"  > {disc.output_excerpt}")
                
                if disc.severity == Severity.CRITICAL:
                    lines.append(f"\n🚨 **ACTION REQUIRED:** This discrepancy requires human review before merge.\n")
                elif disc.severity == Severity.MAJOR:
                    lines.append(f"\n⚠️ **RECOMMENDED:** Human review suggested.\n")
                
                lines.append(f"\n")
    
    lines.append(f"\n---\n")
    
    # Detailed Agent Reviews
    lines.append(f"## Detailed Agent Reviews\n")
    
    for artifact in artifacts:
        agent_anchor = artifact.agent_name.lower().replace(' ', '-').replace('_', '-')
        lines.append(f"### {artifact.agent_name}\n")
        lines.append(f"**Validation Status:** {artifact.validation_status.upper()}\n")
        
        # Split plan and output (assuming they're in the same text with markers)
        plan_text, output_text = _extract_plan_and_output(artifact.plan_text, artifact.output_text)
        
        lines.append(f"#### Review Plan\n")
        lines.append(f"```\n{plan_text}\n```\n")
        
        lines.append(f"#### Review Execution\n")
        lines.append(f"{output_text}\n")
        
        lines.append(f"\n---\n")
    
    # Human Review Required Section
    lines.append(f"## Human Review Required\n")
    
    critical_items = []
    major_items = []
    
    for artifact in artifacts:
        for disc in artifact.discrepancies:
            if disc.severity == Severity.CRITICAL:
                critical_items.append((artifact.agent_name, disc))
            elif disc.severity == Severity.MAJOR:
                major_items.append((artifact.agent_name, disc))
    
    if not critical_items and not major_items:
        lines.append(f"✅ No items require mandatory human review.\n")
    else:
        lines.append(f"The following discrepancies have been flagged for human attention:\n")
        
        if critical_items:
            lines.append(f"\n### 🔴 Critical Items (Must Review)\n")
            for agent_name, disc in critical_items:
                lines.append(f"- **{agent_name}**: {disc.type}")
                lines.append(f"  - {disc.description}\n")
        
        if major_items:
            lines.append(f"\n### 🟡 Major Items (Should Review)\n")
            for agent_name, disc in major_items:
                lines.append(f"- **{agent_name}**: {disc.type}")
                lines.append(f"  - {disc.description}\n")
    
    lines.append(f"\n---\n")
    
    # Footer
    lines.append(f"*Report generated by PR Review Swarm*  ")
    lines.append(f"*Timestamp: {datetime.now().isoformat()}*")
    
    return '\n'.join(lines)


def _get_severity_badge(severity: Severity) -> str:
    """Get a colored badge for severity level."""
    if severity == Severity.CRITICAL:
        return "🔴 CRITICAL"
    elif severity == Severity.MAJOR:
        return "🟡 MAJOR"
    else:
        return "⚪ MINOR"


def _extract_plan_and_output(plan_text: str, output_text: str) -> tuple[str, str]:
    """
    Extract plan and output from agent responses.
    In two-loop agents, the first loop is the plan, second is execution.
    """
    # If they're already separated, return as-is
    if plan_text and output_text and plan_text != output_text:
        return plan_text, output_text
    
    # Otherwise, try to split combined text
    # This is a fallback - ideally we capture them separately
    combined = plan_text or output_text or ""
    
    # Look for common separators
    if "PHASE 2" in combined or "EXECUTION" in combined:
        parts = combined.split("PHASE 2", 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
    
    # If no clear separation, return as-is
    return combined, ""
