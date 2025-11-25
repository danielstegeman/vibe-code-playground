"""Agents package."""

from .security_reviewer import create_security_reviewer
from .code_quality_reviewer import create_code_quality_reviewer
from .test_coverage_reviewer import create_test_coverage_reviewer
from .documentation_reviewer import create_documentation_reviewer
from .qa_validator import create_qa_validator, parse_qa_validation
from .director import create_director


def create_all_reviewers(model_name: str = "gpt-4o") -> list:
    """Create all specialized reviewer agents."""
    return [
        create_security_reviewer(model_name=model_name),
        create_code_quality_reviewer(model_name=model_name),
        create_test_coverage_reviewer(model_name=model_name),
        create_documentation_reviewer(model_name=model_name),
    ]


__all__ = [
    'create_security_reviewer',
    'create_code_quality_reviewer',
    'create_test_coverage_reviewer',
    'create_documentation_reviewer',
    'create_qa_validator',
    'create_director',
    'create_all_reviewers',
    'parse_qa_validation',
]
