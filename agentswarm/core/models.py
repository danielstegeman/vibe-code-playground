"""Data structures for tracking agent review artifacts and validation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Severity(Enum):
    """Severity levels for validation discrepancies."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class Discrepancy:
    """Represents a mismatch between plan and output."""
    type: str  # e.g., "scope_drift", "missed_item", "hallucination"
    severity: Severity
    description: str
    plan_excerpt: str
    output_excerpt: str


@dataclass
class ReviewArtifact:
    """Tracks the complete review artifact for a single agent."""
    agent_name: str
    plan_text: str
    output_text: str
    timestamp: datetime = field(default_factory=datetime.now)
    validation_status: str = "pending"  # pending, validated, flagged
    discrepancies: List[Discrepancy] = field(default_factory=list)
    
    def add_discrepancy(
        self, 
        type: str, 
        severity: Severity, 
        description: str, 
        plan_excerpt: str, 
        output_excerpt: str
    ):
        """Add a discrepancy to this artifact."""
        self.discrepancies.append(
            Discrepancy(
                type=type,
                severity=severity,
                description=description,
                plan_excerpt=plan_excerpt,
                output_excerpt=output_excerpt
            )
        )
        self.validation_status = "flagged"
    
    def has_critical_issues(self) -> bool:
        """Check if artifact has any critical discrepancies."""
        return any(d.severity == Severity.CRITICAL for d in self.discrepancies)
    
    def has_issues(self) -> bool:
        """Check if artifact has any discrepancies."""
        return len(self.discrepancies) > 0
