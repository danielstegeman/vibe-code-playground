"""Main orchestration service for PR review swarm."""

from datetime import datetime
from typing import Optional

from agents import create_all_reviewers, create_qa_validator, create_director, parse_qa_validation
from core.models import ReviewArtifact
from infrastructure.logging import ReviewLogger
from .report_generator import generate_markdown_report


def run_pr_review(
    pr_number: str, 
    pr_description: str, 
    pr_diff: str = None, 
    model_name: str = "gpt-4o",
    output_dir: str = "outputs/reports"
) -> dict:
    """
    Execute the full PR review workflow.
    
    Args:
        pr_number: Pull request number or identifier
        pr_description: Description of the PR
        pr_diff: Optional PR diff content (for future GitHub integration)
        model_name: LLM model to use for all agents
        output_dir: Directory to save the report
    
    Returns:
        Dictionary with success status, report path, artifacts, and director output
    """
    logger = ReviewLogger(verbose=True)
    
    logger.log_header(f"PR REVIEW SWARM - PR #{pr_number}")
    logger.log_progress(f"Starting multi-agent review process...")
    logger.log_progress(f"Using model: {model_name}")
    
    try:
        # Step 1: Create all agents
        logger.log_stage("AGENT INITIALIZATION")
        reviewers = create_all_reviewers(model_name=model_name)
        qa_validator = create_qa_validator(model_name=model_name)
        director = create_director(model_name=model_name)
        logger.log_progress(f"Initialized {len(reviewers)} reviewer agents + QA validator + Director")
        
        # Step 2: Run reviewer agents (two-phase: plan + execute)
        logger.log_stage("REVIEWER EXECUTION")
        artifacts = []
        
        # Build the review task
        diff_section = f'Diff Content:\n{pr_diff}' if pr_diff else ''
        review_task = f"""Pull Request #{pr_number}

Description:
{pr_description}

{diff_section}

Execute your two-phase review:
1. First, create your detailed review plan
2. Then, execute the review following that plan exactly
"""
        
        for reviewer in reviewers:
            agent_name = reviewer.agent_name
            
            # Phase 1: Planning
            logger.log_agent_start(agent_name, "PLANNING")
            plan_response = reviewer.run(review_task)
            logger.log_agent_complete(agent_name, "PLANNING")
            
            # Phase 2: Execution (agent will auto-loop due to max_loops=2)
            # The plan is already in conversation history
            logger.log_agent_start(agent_name, "EXECUTION")
            execution_response = reviewer.run("Now execute your review following the plan you created.")
            logger.log_agent_complete(agent_name, "EXECUTION")
            
            # Create artifact
            artifact = ReviewArtifact(
                agent_name=agent_name,
                plan_text=str(plan_response),
                output_text=str(execution_response),
                timestamp=datetime.now()
            )
            artifacts.append(artifact)
        
        logger.log_progress(f"Completed {len(reviewers)} agent reviews")
        
        # Step 3: QA Validation
        logger.log_validation_start()
        
        # Build QA input with all plans and outputs
        qa_input = _build_qa_input(artifacts)
        qa_output = qa_validator.run(qa_input)
        
        # Parse QA output and update artifacts
        artifacts = parse_qa_validation(str(qa_output), artifacts)
        
        # Log discrepancies
        logger.log_discrepancies(artifacts)
        logger.log_human_review_summary(artifacts)
        
        # Step 4: Director Synthesis
        logger.log_director_start()
        
        # Build director input with all reviews and QA findings
        director_input = _build_director_input(artifacts, str(qa_output))
        director_output = director.run(director_input)
        
        logger.log_progress("Director synthesis complete")
        
        # Step 5: Generate Markdown Report
        report_path = generate_markdown_report(
            pr_number=pr_number,
            pr_description=pr_description,
            artifacts=artifacts,
            qa_output=str(qa_output),
            director_output=str(director_output),
            output_dir=output_dir
        )
        
        logger.log_report_generation(report_path)
        
        # Completion
        logger.log_completion()
        
        return {
            'success': True,
            'report_path': report_path,
            'artifacts': artifacts,
            'director_output': director_output
        }
        
    except Exception as e:
        logger.log_error("PR review failed", e)
        raise


def _build_qa_input(artifacts: list[ReviewArtifact]) -> str:
    """Build input for QA validator from all artifacts."""
    lines = ["Review the following agent plans and outputs for discrepancies:\n"]
    
    for artifact in artifacts:
        lines.append(f"\n{'='*80}")
        lines.append(f"AGENT: {artifact.agent_name}")
        lines.append(f"{'='*80}\n")
        lines.append(f"PLAN (Phase 1):")
        lines.append(f"{artifact.plan_text}\n")
        lines.append(f"\nEXECUTION OUTPUT (Phase 2):")
        lines.append(f"{artifact.output_text}\n")
    
    return '\n'.join(lines)


def _build_director_input(artifacts: list[ReviewArtifact], qa_output: str) -> str:
    """Build input for director from all reviews and QA findings."""
    lines = ["Synthesize the following review findings into a comprehensive final recommendation:\n"]
    
    # Add individual reviews
    lines.append("\n## INDIVIDUAL REVIEWER FINDINGS\n")
    for artifact in artifacts:
        lines.append(f"\n### {artifact.agent_name}")
        lines.append(f"{artifact.output_text}\n")
    
    # Add QA validation findings
    lines.append("\n## QA VALIDATION FINDINGS\n")
    lines.append(qa_output)
    
    lines.append("\n## YOUR TASK\n")
    lines.append("Provide a comprehensive synthesis following your structured format.")
    lines.append("Flag any QA discrepancies that need human review.")
    lines.append("Make a clear final recommendation.")
    
    return '\n'.join(lines)
