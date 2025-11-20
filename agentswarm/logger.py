"""Observability and logging utilities for PR review swarm."""

from colorama import init, Fore, Style
from datetime import datetime
from review_artifact import ReviewArtifact, Severity
import sys

# Initialize colorama for Windows support
init()


class ReviewLogger:
    """Handles colored console logging for review process."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        
    def log_header(self, message: str):
        """Log a header message."""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{message}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    def log_stage(self, stage: str):
        """Log a workflow stage."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{Fore.BLUE}[{timestamp}] 📋 {stage}{Style.RESET_ALL}")
    
    def log_agent_start(self, agent_name: str, phase: str):
        """Log agent execution start."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Fore.GREEN}[{timestamp}] ▶ {agent_name} - {phase}{Style.RESET_ALL}")
    
    def log_agent_complete(self, agent_name: str, phase: str):
        """Log agent execution completion."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Fore.GREEN}[{timestamp}] ✓ {agent_name} - {phase} complete{Style.RESET_ALL}")
    
    def log_progress(self, message: str):
        """Log progress message."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{Fore.WHITE}[{timestamp}] {message}{Style.RESET_ALL}")
    
    def log_validation_start(self):
        """Log QA validation start."""
        self.log_stage("QA VALIDATION")
        print(f"{Fore.YELLOW}🔍 Validating plan-output alignment for all reviewers...{Style.RESET_ALL}\n")
    
    def log_discrepancies(self, artifacts: list[ReviewArtifact]):
        """Log all discrepancies found by QA validator."""
        total_discrepancies = sum(len(a.discrepancies) for a in artifacts)
        
        if total_discrepancies == 0:
            print(f"{Fore.GREEN}✓ All reviewers followed their plans perfectly!{Style.RESET_ALL}\n")
            return
        
        print(f"{Fore.YELLOW}⚠ Found {total_discrepancies} discrepancies requiring attention:{Style.RESET_ALL}\n")
        
        for artifact in artifacts:
            if not artifact.has_issues():
                continue
                
            print(f"{Fore.CYAN}Agent: {artifact.agent_name}{Style.RESET_ALL}")
            
            for disc in artifact.discrepancies:
                severity_color = self._get_severity_color(disc.severity)
                severity_icon = self._get_severity_icon(disc.severity)
                
                print(f"{severity_color}{severity_icon} {disc.severity.value.upper()}: {disc.type}{Style.RESET_ALL}")
                print(f"  Description: {disc.description}")
                print(f"  Plan: \"{disc.plan_excerpt[:100]}...\"")
                print(f"  Output: \"{disc.output_excerpt[:100]}...\"")
                
                if disc.severity == Severity.CRITICAL:
                    print(f"{Fore.RED}  🚨 ACTION REQUIRED: NEEDS HUMAN REVIEW{Style.RESET_ALL}")
                elif disc.severity == Severity.MAJOR:
                    print(f"{Fore.YELLOW}  ⚠️  RECOMMENDED: Human review suggested{Style.RESET_ALL}")
                
                print()
    
    def log_human_review_summary(self, artifacts: list[ReviewArtifact]):
        """Log summary of items needing human review."""
        critical_items = []
        major_items = []
        
        for artifact in artifacts:
            for disc in artifact.discrepancies:
                if disc.severity == Severity.CRITICAL:
                    critical_items.append((artifact.agent_name, disc))
                elif disc.severity == Severity.MAJOR:
                    major_items.append((artifact.agent_name, disc))
        
        if not critical_items and not major_items:
            return
        
        print(f"\n{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}{Style.BRIGHT}🚨 HUMAN REVIEW REQUIRED 🚨{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
        
        if critical_items:
            print(f"{Fore.RED}CRITICAL DISCREPANCIES ({len(critical_items)}):{Style.RESET_ALL}")
            for agent_name, disc in critical_items:
                print(f"  • {agent_name}: {disc.type} - {disc.description}")
            print()
        
        if major_items:
            print(f"{Fore.YELLOW}MAJOR DISCREPANCIES ({len(major_items)}):{Style.RESET_ALL}")
            for agent_name, disc in major_items:
                print(f"  • {agent_name}: {disc.type} - {disc.description}")
            print()
        
        print(f"{Fore.CYAN}Please review these discrepancies in the generated markdown report.{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
    
    def log_director_start(self):
        """Log director synthesis start."""
        self.log_stage("DIRECTOR SYNTHESIS")
        print(f"{Fore.MAGENTA}🎯 Synthesizing all findings into final recommendation...{Style.RESET_ALL}\n")
    
    def log_report_generation(self, filepath: str):
        """Log report generation."""
        self.log_stage("REPORT GENERATION")
        print(f"{Fore.GREEN}📄 Generating markdown review report...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Report saved to: {filepath}{Style.RESET_ALL}\n")
    
    def log_completion(self):
        """Log workflow completion."""
        print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{Style.BRIGHT}✅ PR REVIEW COMPLETE{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
    
    def log_error(self, message: str, exception: Exception = None):
        """Log an error message."""
        print(f"\n{Fore.RED}❌ ERROR: {message}{Style.RESET_ALL}", file=sys.stderr)
        if exception and self.verbose:
            print(f"{Fore.RED}{str(exception)}{Style.RESET_ALL}", file=sys.stderr)
    
    def _get_severity_color(self, severity: Severity) -> str:
        """Get color for severity level."""
        if severity == Severity.CRITICAL:
            return Fore.RED
        elif severity == Severity.MAJOR:
            return Fore.YELLOW
        else:
            return Fore.WHITE
    
    def _get_severity_icon(self, severity: Severity) -> str:
        """Get icon for severity level."""
        if severity == Severity.CRITICAL:
            return "🔴"
        elif severity == Severity.MAJOR:
            return "🟡"
        else:
            return "⚪"
